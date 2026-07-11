import os
import sys
import json
import asyncio
import logging
import warnings
import functools
import random
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from dotenv import load_dotenv

import google.generativeai as genai

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ["GRPC_PYTHON_LOG_LEVEL"] = "ERROR"
load_dotenv()

# --- STRUCTURED LOGGING ---
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {"level": record.levelname, "message": record.getMessage()}
        # Ensure no secrets leak into logs
        if "API_KEY" in log_record["message"]:
            log_record["message"] = log_record["message"].replace(os.getenv("GEMINI_API_KEY", ""), "[REDACTED]")
        return json.dumps(log_record)

logger = logging.getLogger("AgentAPI")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.critical("GEMINI_API_KEY missing from .env")
    sys.exit(1)
genai.configure(api_key=api_key)

# --- EXPONENTIAL BACKOFF ---
def async_retry_with_backoff(max_retries=3, initial_delay=2, backoff_factor=2):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    sleep_time = delay + random.uniform(0, 0.5)
                    logger.warning(f"Transient error, retrying in {sleep_time:.2f}s...")
                    await asyncio.sleep(sleep_time)
                    delay *= backoff_factor
        return wrapper
    return decorator

# --- NATIVE MCP PROTOCOL CLIENT (From Phase 2) ---
class NativeMCPClient:
    def __init__(self, script_path):
        self.script_path = script_path
        self.process = None
        self.msg_id = 1

    async def start(self):
        self.process = await asyncio.create_subprocess_exec(
            sys.executable, "-W", "ignore", self.script_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        await self._send({"jsonrpc": "2.0", "id": self.msg_id, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "api_agent", "version": "1.0"}}})
        await self._wait_for(self.msg_id)
        self.msg_id += 1
        await self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    async def _send(self, payload):
        data = json.dumps(payload) + "\n"
        self.process.stdin.write(data.encode('utf-8'))
        await self.process.stdin.drain()

    async def _wait_for(self, expected_id):
        while True:
            line = await self.process.stdout.readline()
            if not line:
                raise Exception("Server disconnected unexpectedly.")
            try:
                msg = json.loads(line.decode('utf-8'))
                if msg.get("id") == expected_id:
                    if "error" in msg:
                        raise Exception(msg["error"])
                    return msg.get("result")
            except json.JSONDecodeError:
                continue

    async def list_tools(self):
        req_id = self.msg_id
        self.msg_id += 1
        await self._send({"jsonrpc": "2.0", "id": req_id, "method": "tools/list"})
        res = await self._wait_for(req_id)
        return res.get("tools", [])

    async def call_tool(self, name, args):
        req_id = self.msg_id
        self.msg_id += 1
        await self._send({"jsonrpc": "2.0", "id": req_id, "method": "tools/call", "params": {"name": name, "arguments": args}})
        res = await self._wait_for(req_id)
        try:
            return res["content"][0]["text"]
        except Exception:
            return json.dumps(res)

# --- CORE API & AGENT STATE ---
mcp_client = NativeMCPClient("src/mcp_server.py")
agent_tools_schema = []
active_sessions = {} # conversation_id -> Gemini ChatSession

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup: Boots the background MCP server and loads tools before accepting API requests."""
    logger.info("Booting native MCP subprocess server...")
    await mcp_client.start()
    
    raw_tools = await mcp_client.list_tools()
    for t in raw_tools:
        schema = t.get("inputSchema", {})
        raw_properties = schema.get("properties", {})
        cleaned_properties = {}
        for p_name, p_info in raw_properties.items():
            if isinstance(p_info, dict):
                cleaned_properties[p_name] = {k: v for k, v in p_info.items() if k not in ["title", "additionalProperties"]}
            else:
                cleaned_properties[p_name] = p_info

        agent_tools_schema.append({
            "function_declarations": [{
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": {"type": "OBJECT", "properties": cleaned_properties, "required": schema.get("required", [])}
            }]
        })
    logger.info(f"API ready. Discovered tools: {[t['name'] for t in raw_tools]}")
    yield
    # Cleanup on shutdown (Optional)

app = FastAPI(lifespan=lifespan)

# --- MODELS ---
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: str = Field(..., min_length=1)

# --- ERROR HANDLERS ---
@app.exception_handler(RequestValidationError)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Returns a clean 200 response with a failure payload for malformed requests."""
    logger.warning(f"Malformed request payload received on {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "error": "Malformed request. 'message' and 'conversation_id' are required strings.", 
            "status": "failed"
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catches internal failures and returns a clean 500. Never leaks stack traces."""
    logger.error(f"Internal System Fault: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "An internal server error occurred while processing the request.", "status": "failed"}
    )

# --- API ENDPOINT ---
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    logger.info(f"Received request for conversation: {request.conversation_id}")
    
    # 1. State Management (Per-Conversation Memory)
    if request.conversation_id not in active_sessions:
        model = genai.GenerativeModel(model_name="gemini-2.5-flash", tools=agent_tools_schema)
        active_sessions[request.conversation_id] = model.start_chat(enable_automatic_function_calling=False)
    
    chat_session = active_sessions[request.conversation_id]
    
    # Context Guardrail: Trim history if it exceeds 12 messages
    if len(chat_session.history) > 12:
        chat_session.history = chat_session.history[-12:]
        while chat_session.history and chat_session.history[0].role != 'user':
            chat_session.history.pop(0)

    # 2. Execution Loop
    iteration_step = 0
    max_iterations = 5
    execution_trace = []
    
    @async_retry_with_backoff(max_retries=3)
    async def safe_send(payload):
        return await chat_session.send_message_async(payload)

    response = await safe_send(request.message)
    
    while True:
        iteration_step += 1
        if iteration_step > max_iterations:
            execution_trace.append("Guardrail: Max iterations reached.")
            return {"answer": "System Error: Safety limit reached.", "status": "failed", "trace": execution_trace}
        
        tool_call = None
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    tool_call = part.function_call
                    break
        
        if not tool_call:
            break
        
        tool_name = tool_call.name
        tool_args = dict(tool_call.args) if tool_call.args else {}
        execution_trace.append(f"Invoked tool '{tool_name}' with args: {tool_args}")
        
        try:
            text_result = await mcp_client.call_tool(tool_name, tool_args)
            tool_result = json.loads(text_result)
        except Exception as e:
            tool_result = {"error": str(e), "success": False}
        
        feedback = genai.protos.Content(
            parts=[genai.protos.Part(function_response=genai.protos.FunctionResponse(name=tool_name, response={"result": tool_result}))]
        )
        response = await safe_send(feedback)

    logger.info(f"Successfully processed response for conversation: {request.conversation_id}")
    return {
        "answer": response.text,
        "status": "success",
        "trace": execution_trace
    }