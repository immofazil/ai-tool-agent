import json
import logging
from mcp.server.fastmcp import FastMCP

# Setup clean logging
logging.basicConfig(level=logging.INFO, format='[SERVER] %(message)s')

# Initialize FastMCP
mcp = FastMCP("Day2-Tools-Server")

@mcp.tool()
def calculate(expression: str) -> str:
    """Evaluates a basic mathematical expression string safely.
    
    Args:
        expression: The arithmetic string containing numbers and operators (e.g., "41 * 2").
    """
    logging.info(f"Executing calculate tool with expression: {expression}")
    clean_expr = expression.replace(" ", "")
    
    # Week 4 Guardrail: Validation
    if not all(char in "0123456789+-*/.()" for char in clean_expr):
        return json.dumps({"error": "Invalid character check failed.", "success": False})
    
    try:
        result = eval(clean_expr, {"__builtins__": None}, {})
        return json.dumps({"expression": expression, "result": float(result), "success": True})
    except Exception as err:
        return json.dumps({"error": str(err), "success": False})

@mcp.tool()
def search_notes(query: str) -> str:
    """Searches local notes for specific keywords.
    
    Args:
        query: The search term to locate.
    """
    logging.info(f"Executing search_notes tool with query: {query}")
    # Mocked database response for stability
    if "dubai" in query.lower() or "heat" in query.lower():
        return json.dumps({"matches": ["Dubai heat threshold is 45 degrees."], "success": True})
    return json.dumps({"matches": ["No matching notes found."], "success": True})

if __name__ == "__main__":
    print("==================================================")
    print("  STARTING MCP SERVER ON HTTP://LOCALHOST:8000/SSE")
    print("  Leave this terminal open and running.")
    print("==================================================")
    # Run via Server-Sent Events (SSE) network protocol
    mcp.run(transport="sse")