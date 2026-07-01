import os
import sys
import json
import logging
from mcp.server.fastmcp import FastMCP

# --- STEP 1: CONFIGURE STRUCTURED JSON LOGGING ---
class JsonFormatter(logging.Formatter):
    """Custom formatter to output logs as structured JSON strings."""
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "component": "MCP_Server_Custom",
            "message": record.getMessage()
        }
        return json.dumps(log_record)

# Initialize server-side logger
logger = logging.getLogger("MCP_Server")
handler = logging.StreamHandler(sys.stderr)  # CRITICAL: MCP servers MUST log to stderr. Stdout is reserved for protocol messages.
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# --- STEP 2: INITIALIZE THE MCP SERVER ---
# FastMCP automatically creates protocol schemas using function signatures and docstrings.
mcp = FastMCP("Custom-Week4-Tools-Server")

# --- STEP 3: EXPOSE THE CALCULATE TOOL ---
@mcp.tool()
def calculate(expression: str) -> str:
    """Evaluates a basic mathematical expression string safely.

    Args:
        expression: The arithmetic string containing numbers and operators (e.g., "41 * 2" or "100 / 5").
    """
    # Structured logging of incoming call properties
    logger.info(f"Incoming call: tool='calculate', args={{'expression': '{expression}'}}, status='RECEIVED'")

    if not expression or not isinstance(expression, str):
        logger.info("Tool execution finalized: tool='calculate', status='VALIDATION_FAILED'")
        return json.dumps({"error": "Missing or malformed required string parameter: 'expression'", "success": False})

    # Sanitize and strip spaces
    clean_expr = expression.replace(" ", "")

    # Hard safety whitelist guardrail from Week 4 logic
    if not all(char in "0123456789+-*/.()" for char in clean_expr):
        logger.info("Tool execution finalized: tool='calculate', status='GUARDRAIL_INTERCEPTED'")
        return json.dumps({"error": "Invalid character check failed. Only basic numbers and operations are allowed.", "success": False})

    try:
        # Evaluate clean arithmetic literals safely
        result = eval(clean_expr, {"__builtins__": None}, {})
        logger.info("Tool execution finalized: tool='calculate', status='SUCCESS'")
        return json.dumps({"expression": expression, "result": float(result), "success": True})
    except Exception as eval_err:
        logger.info("Tool execution finalized: tool='calculate', status='EVALUATION_ERROR'")
        return json.dumps({"expression": expression, "error": f"Math evaluation error: {str(eval_err)}", "success": False})

# --- STEP 4: EXPOSE THE SEARCH NOTES TOOL ---
@mcp.tool()
def search_notes(query: str) -> str:
    """Searches a local text file for a specific keyword matching system thresholds.

    Args:
        query: The search term or keyword to locate within the local text note lines.
    """
    logger.info(f"Incoming call: tool='search_notes', args={{'query': '{query}'}}, status='RECEIVED'")

    if not query or not isinstance(query, str):
        logger.info("Tool execution finalized: tool='search_notes', status='VALIDATION_FAILED'")
        return json.dumps({"error": "Missing or malformed required string parameter: 'query'", "success": False})

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "notes.txt")
    
    # Pre-execution file system validation guardrail
    if not os.path.exists(file_path):
        logger.info("Tool execution finalized: tool='search_notes', status='FILE_NOT_FOUND'")
        return json.dumps({"error": f"Local storage file '{file_path}' could not be located.", "success": False})

    try:
        # Read data from the local text file
        with open(file_path, "r", encoding="utf-8") as f:
            mock_notes_file = f.readlines()

        query_clean = query.lower().strip()
        matches = [note.strip() for note in mock_notes_file if query_clean in note.lower()]

        logger.info("Tool execution finalized: tool='search_notes', status='SUCCESS'")
        return json.dumps({"query": query, "matches": matches, "count": len(matches), "success": True})
        
    except Exception as file_err:
        logger.info("Tool execution finalized: tool='search_notes', status='IO_ERROR'")
        return json.dumps({"error": f"Failed to safely read local index: {str(file_err)}", "success": False})

if __name__ == "__main__":
    # Start the standard stdio server loop
    mcp.run(transport="stdio")