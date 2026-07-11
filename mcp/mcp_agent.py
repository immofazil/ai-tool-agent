import os
import sys
import json
import asyncio
import warnings
import logging
from dotenv import load_dotenv

# Suppress ALL Google and Python warnings to keep the terminal perfectly clean
warnings.filterwarnings("ignore")
os.environ["GRPC_PYTHON_LOG_LEVEL"] = "ERROR"

import google.generativeai as genai

load_dotenv()

# --- LOGGING SETUP ---
class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({"level": record.levelname, "agent_trace": record.getMessage()})

logger = logging.getLogger("Agent")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY missing from .env")
    sys.exit(1)

genai.configure(api_key=api_key)

# --- PURE NATIVE MCP PROTOCOL CLIENT ---
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
        
        await self._send({
            "jsonrpc": "2.0", "id": self.msg_id, "method": "initialize", 
            "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "agent", "version": "1.0"}}
        })
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

# --- WEEK 4 AGENT ORCHESTRATOR ---
class MCPAgent:
    def __init__(self, mcp_client, raw_tools, max_iterations=5):
        self.mcp_client = mcp_client
        self.max_iterations = max_iterations
        
        gemini_tools = []
        for t in raw_tools:
            schema = t.get("inputSchema", {})
            raw_properties = schema.get("properties", {})
            
            cleaned_properties = {}
            for param_name, param_info in raw_properties.items():
                if isinstance(param_info, dict):
                    cleaned_info = {k: v for k, v in param_info.items() if k not in ["title", "additionalProperties"]}
                    cleaned_properties[param_name] = cleaned_info
                else:
                    cleaned_properties[param_name] = param_info

            func_decl = {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": {
                    "type": "OBJECT",
                    "properties": cleaned_properties,
                    "required": schema.get("required", [])
                }
            }
            gemini_tools.append({"function_declarations": [func_decl]})
            
        self.model = genai.GenerativeModel(model_name="gemini-2.5-flash", tools=gemini_tools)
        self.chat = self.model.start_chat(enable_automatic_function_calling=False)
        logger.info(f"Agent initialized. Tools loaded: {[t['name'] for t in raw_tools]}")

    async def process_query(self, user_prompt: str) -> str:
        iteration_step = 0
        try:
            response = await self.chat.send_message_async(user_prompt)
            
            while True:
                iteration_step += 1
                if iteration_step > self.max_iterations:
                    return "System Error: Safety limit reached."
                
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
                logger.info(f"Trace: Routing to tool '{tool_name}' with args {tool_args}")
                
                try:
                    text_result = await self.mcp_client.call_tool(tool_name, tool_args)
                    tool_result = json.loads(text_result)
                except Exception as execution_crash:
                    tool_result = {"error": str(execution_crash), "success": False}
                
                feedback = genai.protos.Content(
                    parts=[genai.protos.Part(function_response=genai.protos.FunctionResponse(name=tool_name, response={"result": tool_result}))]
                )
                response = await self.chat.send_message_async(feedback)

            return response.text

        except Exception as err:
            logger.error(f"Processing breakdown: {str(err)}")
            return "Graceful Recovery Notification: Internal failure stopped this request."

# --- EXECUTION RUNTIME ---
async def start_environment():
    print("\n" + "="*70)
    print("   HARDENED MCP AGENT RUNTIME (PURE NATIVE)")
    print("   Attempting handshake with background server...")
    
    try:
        client = NativeMCPClient("src/mcp_server.py")
        await client.start()
        
        tools = await client.list_tools()
        print(f"   [SUCCESS] Connected to Server. Discovered {len(tools)} Tools.")
        print("="*70 + "\n")
        
        agent = MCPAgent(client, tools)
        
        automated_query = "Calculate 41 * 2"
        print(f"User Input >>> {automated_query}")
        
        agent_response = await agent.process_query(automated_query)
        print(f"\n[Agent Response]:\n{agent_response}\n")
        
        print("="*70)
        print("   SUCCESS! TAKE SCREENSHOT 1 NOW.")
        print("="*70 + "\n")
        
    except Exception as server_err:
        print("\n" + "="*70)
        print("[SYSTEM FAULT] SERVER-UNREACHABLE GRACEFUL FALLBACK")
        print("The core tool server is offline, crashed, or unreachable.")
        print(f"Details: {str(server_err)}")
        print("="*70 + "\n")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(start_environment())