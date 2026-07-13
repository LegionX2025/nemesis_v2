import os
import json
import logging
import asyncio
from typing import Dict, Any, List

logger = logging.getLogger("NEMESIS_MCP_GATEWAY")

# Optional import, graceful degradation if mcp SDK is missing
try:
    from mcp import ClientSession
    from mcp.client.sse import sse_client
    import mcp.types as types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("mcp SDK not found. Bitquery MCP integration will be disabled.")

class BitqueryMCPGateway:
    def __init__(self):
        self.base_url = "https://mcp.bitquery.io"
        self.token = os.getenv("BITQUERY_APIV2_TOKEN", "")
        self.session = None
        self.exit_stack = None
        self.tools = []
        self.is_connected = False

    async def connect(self):
        if not MCP_AVAILABLE:
            return False
            
        if not self.token:
            logger.warning("No BITQUERY_APIV2_TOKEN found. MCP connection requires authentication.")
            return False

        # Bitquery allows auth via URL parameter ?token=...
        url_with_auth = f"{self.base_url}/?token={self.token}"

        try:
            from contextlib import AsyncExitStack
            self.exit_stack = AsyncExitStack()
            
            # Connect via SSE transport
            sse_transport = await self.exit_stack.enter_async_context(sse_client(url_with_auth))
            
            # Initialize Session
            self.session = await self.exit_stack.enter_async_context(ClientSession(sse_transport[0], sse_transport[1]))
            await self.session.initialize()
            
            self.is_connected = True
            logger.info("Successfully connected to Bitquery MCP Server.")
            
            # Fetch available tools
            response = await self.session.list_tools()
            self.tools = response.tools
            logger.info(f"Loaded {len(self.tools)} tools from Bitquery MCP.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Bitquery MCP: {str(e)}")
            if self.exit_stack:
                await self.exit_stack.aclose()
            return False

    async def disconnect(self):
        self.is_connected = False
        if self.exit_stack:
            await self.exit_stack.aclose()
            logger.info("Bitquery MCP connection closed.")

    def get_gemini_tools(self) -> List[Dict[str, Any]]:
        """
        Translates MCP tool schemas into Gemini native tool formats.
        """
        gemini_tools = []
        for tool in self.tools:
            # We map MCP jsonschema to Gemini's format
            func_decl = {
                "name": tool.name.replace("-", "_"),
                "description": tool.description or f"Executes {tool.name}",
                "parameters": tool.inputSchema
            }
            gemini_tools.append(func_decl)
            
        return gemini_tools

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Executes a remote MCP tool and returns the result string.
        """
        if not self.is_connected or not self.session:
            return "Error: MCP Client is not connected."
            
        try:
            logger.info(f"Executing MCP Tool: {tool_name} with args: {arguments}")
            result = await self.session.call_tool(tool_name, arguments)
            
            if result.isError:
                return f"MCP Tool Error: {result.content}"
                
            # Parse text content
            texts = [c.text for c in result.content if hasattr(c, 'text')]
            return "\n".join(texts)
            
        except Exception as e:
            logger.error(f"MCP Tool Execution Failed: {str(e)}")
            return f"System Error executing tool: {str(e)}"

# Singleton instance for the FastAPI lifecycle
bitquery_mcp = BitqueryMCPGateway()
