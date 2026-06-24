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

# ==========================================
# STRUCTURED JSON LOGGING CONFIGURATION
# ==========================================
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


# ==========================================
# RELIABILITY: Exponential Backoff Retry
# ==========================================
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


# ==========================================
# AUTONOMOUS TOOL DEFINITION
# ==========================================
def get_current_weather(city: str) -> dict:
    """Gets the current weather and temperature conditions for a given city.
    
    Args:
        city: The name of the city to lookup (e.g., "Tokyo", "Paris", "Dubai").
    """
    mock_weather_db = {
        "tokyo": {"condition": "Sunny", "temperature": "26°C", "humidity": "45%"},
        "paris": {"condition": "Rainy", "temperature": "14°C", "humidity": "80%"},
        "dubai": {"condition": "Hot and Clear", "temperature": "41°C", "humidity": "20%"},
        "london": {"condition": "Cloudy", "temperature": "18°C", "humidity": "70%"}
    }
    
    city_clean = city.lower().strip()
    logger.info(f"Executing tool 'get_current_weather' for parameters: city='{city}'")
    
    if city_clean in mock_weather_db:
        return {"city": city, **mock_weather_db[city_clean], "success": True}
        
    return {
        "city": city, 
        "condition": "Unknown", 
        "temperature": "N/A", 
        "error": f"City '{city}' not found in mock data.", 
        "success": False
    }

# Mapping registry for local function routing
AVAILABLE_TOOLS = {
    "get_current_weather": get_current_weather
}


# ==========================================
# AGENT ORCHESTRATION ENGINE
# ==========================================
class AutonomousAgent:
    def __init__(self):
        # Bind the Python function directly; schemas are inferred automatically
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            tools=[get_current_weather]
        )
        logger.info("Agent engine initialized successfully with tool: 'get_current_weather'")

    @retry_with_backoff(max_retries=3)
    def _safe_llm_call(self, history):
        """Isolated model invocation wrapped with our backoff safety net."""
        return self.model.generate_content(history)

    def process_query(self, user_prompt: str) -> str:
        """Manages the full function routing loop or direct answers."""
        logger.info(f"Processing new manual user interaction: '{user_prompt}'")
        
        if not user_prompt.strip():
            logger.error("Input validation failed: Provided query string is blank.")
            return "Error: Input cannot be empty. Please ask a valid question."

        # FIXED: Initialize history as a clean, native Python dictionary
        messages = [
            {
                "role": "user",
                "parts": [user_prompt]
            }
        ]

        try:
            logger.info("Dispatching initial contextual prompt payload to model...")
            response = self._safe_llm_call(messages)
            
            # Extract potential tool execution requests generated by the model
            function_calls = response.candidates[0].function_calls
            
            if function_calls:
                tool_call = function_calls[0]
                tool_name = tool_call.name
                tool_args = dict(tool_call.args)
                
                logger.info(f"Model made routing decision: Tool Call Required -> '{tool_name}' with args: {tool_args}")
                
                if tool_name in AVAILABLE_TOOLS:
                    # Append the model's response to keep structural history intact
                    messages.append(response.candidates[0].content)
                    
                    # Execute the local tool
                    try:
                        tool_result = AVAILABLE_TOOLS[tool_name](**tool_args)
                        logger.info("Tool execution successfully completed by local runner.")
                    except Exception as tool_exec_err:
                        logger.error(f"Runtime execution crash inside tool '{tool_name}': {str(tool_exec_err)}", exc_info=True)
                        return f"Failed to complete task due to a tool crash: {str(tool_exec_err)}"
                    
                    # FIXED: Formulate function response using a native Python dictionary structure
                    function_response_payload = {
                        "role": "function",
                        "parts": [{
                            "function_response": {
                                "name": tool_name,
                                "response": {"result": tool_result}
                            }
                        }]
                    }
                    messages.append(function_response_payload)
                    
                    # Send execution context back to the model for final synthesis
                    logger.info("Returning tool execution payload to model for summary generation...")
                    final_response = self._safe_llm_call(messages)
                    return final_response.text
                else:
                    logger.error(f"Model requested unmapped tool variant: '{tool_name}'. Routing canceled.")
                    return f"Error: The model tried to call a tool that is not registered ('{tool_name}')."
            
            else:
                logger.info("Model made routing decision: No tool needed. Processing prompt directly.")
                return response.text

        except Exception as main_loop_error:
            logger.error(f"Critical agent processing failure: {str(main_loop_error)}", exc_info=True)
            return "An internal system error prevented the agent from fulfilling this request."


if __name__ == "__main__":
    agent = AutonomousAgent()
    
    print("\n" + "="*60)
    print("   AUTONOMOUS SINGLE-TOOL AGENT RUNTIME ENVIRONMENT")
    print("   Type your prompt below to observe structural logging decisions.")
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