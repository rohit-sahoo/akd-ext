"""FastMCP Server for akd-ext tools."""

from fastmcp import FastMCP

from akd_ext.mcp.registry import mcp_tool_registry
from akd_ext.mcp.converter import tool_converter, register_mcp_tool

# Create MCP server
mcp = FastMCP("akd-ext-tools")


def register_all_tools():
    """
    Auto-discover and register all @mcp_tool decorated classes.

    This function imports the tools module to trigger decorator registration,
    then converts and registers each tool with the FastMCP server.

    Example:
        register_all_tools()  # All @mcp_tool classes now available via MCP
    """
    from akd_ext import tools

    # Get all registered tool classes from singleton registry
    tool_classes = mcp_tool_registry.get_tools()

    for tool_class in tool_classes:
        tool = tool_class()
        # Convert tool to FastMCP compatible function
        mcp_func = tool_converter(tool)
        # Register tool with FastMCP server      
        register_mcp_tool(mcp_func, mcp)     


register_all_tools()


if __name__ == "__main__":
    mcp.run()
