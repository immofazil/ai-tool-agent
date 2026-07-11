import warnings
# Suppress the underlying library deprecation alerts to keep terminal logs clean
warnings.simplefilter(action='ignore', category=FutureWarning)

import os
import sys
import time
import json
import random
import logging
import functools
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()


class JsonFormatter(logging.Formatter):
    """Custom formatter to output logs as structured JSON strings."""
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage()
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

# Set up the logger
logger = logging.getLogger("AI_Agent")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Verify API Key existence
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.critical("GEMINI_API_KEY is missing from your .env file!")
    raise ValueError("API Key not found.")

genai.configure(api_key=api_key)



def retry_with_backoff(max_retries=3, initial_delay=2, backoff_factor=2):
    """Decorator to catch transient API anomalies using exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"API operation critically failed after {max_retries} attempts.", exc_info=True)
                        raise e
                    
                    jitter = random.uniform(0, 0.5)
                    sleep_time = delay + jitter
                    
                    logger.warning(
                        f"Temporary API error encountered. Retrying step (Attempt {attempt + 2}/{max_retries}) in {sleep_time:.2f}s... Error: {str(e)}"
                    )
                    time.sleep(sleep_time)
                    delay *= backoff_factor
        return wrapper
    return decorator


def get_weather(city: str) -> dict:
    """Gets the current weather condition and numeric temperature for a given city.
    
    Args:
        city: The name of the city to lookup (e.g., "Tokyo", "Paris", "Dubai").
    """
    mock_weather_db = {
        "tokyo": {"condition": "Sunny", "temperature": 26, "humidity": "45%"},
        "paris": {"condition": "Rainy", "temperature": 14, "humidity": "80%"},
        "dubai": {"condition": "Hot and Clear", "temperature": 41, "humidity": "20%"},
        "london": {"condition": "Cloudy", "temperature": 18, "humidity": "70%"}
    }
    
    if not city:
        raise ValueError("Missing required positional parameter: 'city'")
        
    city_clean = str(city).lower().strip()
    logger.info(f"Executing tool 'get_weather' for parameter: city='{city}'")
    
    if city_clean in mock_weather_db:
        return {"city": city, **mock_weather_db[city_clean], "success": True}
        
    return {"city": city, "error": f"City '{city}' not found in mock weather database.", "success": False}


def calculate(expression: str) -> dict:
    """Evaluates a basic mathematical expression string safely.
    
    Args:
        expression: The arithmetic string to calculate containing numbers and operators (e.g., "41 * 2" or "100 / 5").
    """
    if not expression:
        raise ValueError("Missing required positional parameter: 'expression'")
        
    logger.info(f"Executing tool 'calculate' for parameter: expression='{expression}'")
    
    # Sanitize and strip spaces
    clean_expr = str(expression).replace(" ", "")
    
    # Hard safety whitelist guardrail to avoid arbitrary execution exploits
    if not all(char in "0123456789+-*/.()" for char in clean_expr):
        return {"error": "Invalid character check failed. Only basic numbers and operations are allowed.", "success": False}
        
    try:
        # Evaluate clean arithmetic literals safely
        result = eval(clean_expr, {"__builtins__": None}, {})
        return {"expression": expression, "result": float(result), "success": True}
    except Exception as eval_err:
        return {"expression": expression, "error": f"Math evaluation error: {str(eval_err)}", "success": False}


def search_notes(query: str) -> dict:
    """Searches local personal text notes and reminders for a specific keyword matching threshold values.
    
    Args:
        query: The search term or keyword to locate within the local text files.
    """
    if not query:
        raise ValueError("Missing required positional parameter: 'query'")
        
    logger.info(f"Executing tool 'search_notes' for parameter: query='{query}'")
    
    mock_notes_file = [
        "Reminder: If Dubai field work heat calculation calculation hits 82 units, halt outdoor projects.",
        "Server room thresholds: Maximum safe system calculation cooling tolerance is 100 units.",
        "Tokyo vacation notes: Hotel reservations are validated up to 300 dollars max capacity.",
        "General notes: Weather parameters under 50 are considered perfectly safe for execution."
    ]
    
    query_clean = str(query).lower().strip()
    matches = [note for note in mock_notes_file if query_clean in note.lower()]
    
    return {"query": query, "matches": matches, "count": len(matches), "success": True}


# Mapping registry for agent orchestration routing
AVAILABLE_TOOLS = {
    "get_weather": get_weather,
    "calculate": calculate,
    "search_notes": search_notes
}



class AutonomousAgent:
    def __init__(self, max_history_messages=12, max_iterations=5):
        # Register all 3 tools with the generative context
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            tools=[get_weather, calculate, search_notes]
        )
        self.max_history_messages = max_history_messages
        self.max_iterations = max_iterations # Hard ceiling limit guardrail configuration
        
        # Initialize a persistent chat session to maintain history across turns
        self.chat = self.model.start_chat(enable_automatic_function_calling=False)
        logger.info(f"Agent engine initialized with 3 tools, running memory, and safety limit ({max_iterations} loops).")

    def enforce_history_guard(self):
        """Trims the oldest messages from history to prevent unbounded token growth."""
        if len(self.chat.history) > self.max_history_messages:
            while len(self.chat.history) > self.max_history_messages:
                self.chat.history.pop(0)
            
            while self.chat.history and self.chat.history[0].role != 'user':
                self.chat.history.pop(0)
                
            logger.info(f"History guard triggered. Trimmed context to {len(self.chat.history)} elements.")

    @retry_with_backoff(max_retries=3)
    def _safe_send_message(self, chat_session, payload):
        """Isolated model invocation wrapped with our backoff safety net."""
        return chat_session.send_message(payload)

    def process_query(self, user_prompt: str) -> str:
        """Manages an infinite multi-step tool sequence loop until final synthesis is reached."""
        logger.info(f"Processing user interaction: '{user_prompt}'")
        
        if not user_prompt.strip():
            logger.error("Input validation failed: Provided query string is blank.")
            return "Error: Input cannot be empty. Please ask a valid question."

        # Enforce history limit before sending new prompts to avoid context window explosion
        self.enforce_history_guard()
        
        # Track the execution trace sequence path metrics
        iteration_step = 0
        
        try:
            logger.info("Dispatching prompt to model using persistent chat session...")
            response = self._safe_send_message(self.chat, user_prompt)
            
            # Continuous agent loop execution block to support multi-step tool combinations
            while True:
                iteration_step += 1
                
                # GUARDRAIL 1: Max-Iteration limit execution check to break infinite loops
                if iteration_step > self.max_iterations:
                    logger.error(f"Guardrail Triggered: Execution exceeded step threshold ({self.max_iterations}). Stopping loop.")
                    return (
                        f"System Error: The agent loop was stopped automatically because it exceeded its safety limit of "
                        f"{self.max_iterations} operational steps. This guardrail prevents runaway billing and infinite loops."
                    )
                
                tool_call = None
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if part.function_call:
                            tool_call = part.function_call
                            break
                
                # Base Case Breakout: If the model provides an answer without requesting a tool, exit the loop
                if not tool_call:
                    logger.info(f"Model trace step {iteration_step}: No tool needed. Generating final answer text.")
                    break
                
                tool_name = tool_call.name
                
                try:
                    tool_args = dict(tool_call.args) if tool_call.args else {}
                except Exception as parse_err:
                    logger.warning(f"Trace step {iteration_step}: Argument parsing failed: {str(parse_err)}")
                    tool_args = {}

                logger.info(f"Trace Step {iteration_step} -> Model Routing Decision: Tool Call Required -> '{tool_name}' with args: {tool_args}")
                
                if tool_name in AVAILABLE_TOOLS:
                    # GUARDRAIL 2: Pre-execution Input Validation and Parameter Repair
                    validation_passed = True
                    validation_error_msg = ""
                    
                    if tool_name == "get_weather" and "city" not in tool_args:
                        validation_passed = False
                        validation_error_msg = "Missing required argument: 'city'. Please re-request with a valid city parameter string."
                    elif tool_name == "calculate" and "expression" not in tool_args:
                        validation_passed = False
                        validation_error_msg = "Missing required argument: 'expression'. Please re-request with a valid mathematical expression."
                    elif tool_name == "search_notes" and "query" not in tool_args:
                        validation_passed = False
                        validation_error_msg = "Missing required argument: 'query'. Please re-request with a valid text query keyword."

                    if not validation_passed:
                        logger.warning(f"Guardrail Input Validation Intercepted Malformed Request: {validation_error_msg}")
                        tool_result = {"error": f"InputValidationError: {validation_error_msg}", "success": False}
                    else:
                        # Execute tool wrapped inside local fault tracking to prevent application engine crashes
                        try:
                            tool_result = AVAILABLE_TOOLS[tool_name](**tool_args)
                            logger.info(f"Trace step {iteration_step}: Tool '{tool_name}' execution completed successfully.")
                        except Exception as execution_crash:
                            # Catch type mismatches cleanly and feed errors back to the AI context to handle
                            logger.error(f"Runtime parameter fault inside tool '{tool_name}': {str(execution_crash)}")
                            tool_result = {
                                "error": f"BadArgumentFault: Validation failed inside tool code. Reason: {str(execution_crash)}",
                                "success": False
                            }
                    
                    # Package tool response using protobuf structures
                    function_response_payload = genai.protos.Content(
                        parts=[
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=tool_name,
                                    response={"result": tool_result}
                                )
                            )
                        ]
                    )
                    
                    # Feed execution result back to the chat history to see what the model chooses to do next
                    logger.info(f"Trace step {iteration_step}: Returning tool '{tool_name}' results payload back to model.")
                    response = self._safe_send_message(self.chat, function_response_payload)
                    
                else:
                    logger.error(f"Model requested unmapped tool variant: '{tool_name}'. Overriding execution path.")
                    error_payload = genai.protos.Content(
                        parts=[
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=tool_name,
                                    response={"result": {"error": "Tool is unregistered in framework.", "success": False}}
                                )
                            )
                        ]
                    )
                    response = self._safe_send_message(self.chat, error_payload)

            return response.text

        except Exception as main_loop_error:
            # GUARDRAIL 3: Graceful Final Fallback - Never expose raw stack trace dumps directly to user responses
            logger.error(f"Critical agent processing loop breakdown failure: {str(main_loop_error)}", exc_info=True)
            return (
                f"Graceful Recovery Notification: An internal system failure stopped this request context from processing safely. "
                f"The core orchestration loop has logged full trace properties to our structural backend analyzer. Please retry your request."
            )


if __name__ == "__main__":
    agent = AutonomousAgent()
    
    print("\n" + "="*60)
    print("   HARDENED AUTONOMOUS MULTI-TOOL AGENT RUNTIME")
    print("   Available Tools: [get_weather, calculate, search_notes]")
    print("   Type your prompt below to observe sequential operations.")
    print("   Type 'exit' or 'quit' to terminate the environment.")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("\nUser Input >>> ")
            if user_input.lower().strip() in ['exit', 'quit']:
                print("\nShutting down Agent runtime context. Goodbye.")
                break
                
            agent_response = agent.process_query(user_input)
            print(f"\n[Agent Response]:\n{agent_response}")
            
        except KeyboardInterrupt:
            print("\nShutting down agent runtime context. Goodbye.")
            break