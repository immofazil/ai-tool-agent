import asyncio
import json
import logging
import os
import sys
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()

# Configure structured JSON logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "component": "MCP_Client_Core", "message": "%(message)s"}',
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("MCP_Client_Core")

async def call_tool_with_backoff(session, tool_name, arguments, max_retries=3, initial_delay=2):
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[Attempt {attempt}/{max_retries}] Sending execution request to tool '{tool_name}'...")
            result = await session.call_tool(name=tool_name, arguments=arguments)
            return result
        except Exception as e:
            logger.warning(f"Tool execution failed on attempt {attempt}: {str(e)}")
            if attempt == max_retries:
                raise e
            await asyncio.sleep(delay)
            delay *= 2

def log_exception_recursive(err):
    if hasattr(err, 'exceptions'):
        for sub_err in err.exceptions:
            log_exception_recursive(sub_err)
    else:
        logger.error(f"True Root Cause Found: {type(err).__name__} - {str(err)}")

async def run_resilient_mcp_client():
    # PYTHON-NATIVE EXECUTION: Bypasses Node/Npx entirely using your current interpreter
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server_fetch"],
        env=dict(os.environ)
    )
    
    logger.info("Initializing connection sequence to external MCP Fetch Server...")
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            logger.info("Transport pipe established successfully. Booting protocol handshake...")
            
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                logger.info("Handshake complete. Client-Server session is fully active.")
                
                # --- PHASE 1: TOOL DISCOVERY ---
                logger.info("Triggering tool discovery routine...")
                discovered_tools = await session.list_tools()
                available_names = [tool.name for tool in discovered_tools.tools]
                logger.info(f"Discovery complete! Server exposed capabilities: {json.dumps(available_names)}")
                
                # --- PHASE 2: TOOL EXECUTION ---
                target_url = "https://example.com"
                tool_output = await call_tool_with_backoff(
                    session=session,
                    tool_name="fetch",
                    arguments={"url": target_url}
                )
                
                clean_payload = tool_output.content[0].text.replace('\n', ' ')
                logger.info(f"Pipeline successful. Received result payload: {json.dumps(clean_payload)}")
                
    except Exception as e:
        log_exception_recursive(e)

if __name__ == "__main__":
    # Ensure Windows handles background process streams cleanly
    if sys.platform == 'win32':
        if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
    asyncio.run(run_resilient_mcp_client())