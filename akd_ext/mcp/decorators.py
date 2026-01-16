"""Decorators for MCP tool registration."""

from typing import Type
from akd.tools._base import BaseTool

# Registry for all @mcp_tool decorated classes
_MCP_TOOL_REGISTRY: list[Type[BaseTool]] = []


def mcp_tool(cls: Type[BaseTool]) -> Type[BaseTool]:
    """
    Decorator to mark a BaseTool class for automatic MCP registration.
    
    Usage:
        @mcp_tool
        class MyTool(BaseTool):
            ...
    """
    if not issubclass(cls, BaseTool):
        raise TypeError(f"@mcp_tool can only be applied to BaseTool subclasses, got {cls}")
    
    # Mark class as MCP tool
    cls._is_mcp_tool = True
    
    # Register in global registry
    if cls not in _MCP_TOOL_REGISTRY:
        _MCP_TOOL_REGISTRY.append(cls)
    
    return cls


def get_mcp_tools() -> list[Type[BaseTool]]:
    """Get all classes decorated with @mcp_tool."""
    return _MCP_TOOL_REGISTRY.copy()
