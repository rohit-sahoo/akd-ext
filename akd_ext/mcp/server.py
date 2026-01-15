from fastmcp import FastMCP

from akd_ext.tools.reverse import ReverseTool
from akd_ext.mcp.converter import toolConverter

# Create MCP server
mcp = FastMCP("akd-ext-tools")

# Auto-register tools
def register_all_tools():
    tools = [
        ReverseTool(),
    ]
    for tool in tools:
        toolConverter(tool, mcp)

register_all_tools()

# Entry point
if __name__ == "__main__":
    mcp.run()
