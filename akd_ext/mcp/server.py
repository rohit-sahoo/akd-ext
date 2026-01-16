from fastmcp import FastMCP

from akd_ext.mcp.decorators import get_mcp_tools
from akd_ext.mcp.converter import toolConverter

# Create MCP server
mcp = FastMCP("akd-ext-tools")


def register_all_tools():
    """Auto-discover and register all @mcp_tool decorated classes."""
    # Import tools module to trigger decorator registration
    from akd_ext import tools  # noqa: F401
    
    # Get all decorated tool classes
    tool_classes = get_mcp_tools()
    
    # Instantiate and register each tool
    for tool_class in tool_classes:
        tool = tool_class()
        toolConverter(tool, mcp)


register_all_tools()


if __name__ == "__main__":
    mcp.run()
