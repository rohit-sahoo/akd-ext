from typing import Callable
from inspect import Signature, Parameter
from fastmcp import FastMCP
from akd.tools._base import BaseTool


def toolConverter(tool: BaseTool, mcp: FastMCP | None = None) -> Callable:
    """Convert akd BaseTool to FastMCP tool."""
    tool_name = tool.name or tool.__class__.__name__
    tool_description = tool.description or ""
    InputModel = tool.input_schema

    # Build function signature from InputModel fields
    field_info = InputModel.model_fields
    param_names = list(field_info.keys())
    param_kwargs = ", ".join(f"{name}={name}" for name in param_names)
    
    # Create function with explicit parameters
    code = f"""async def mcp_tool_wrapper({', '.join(param_names)}):
    params = InputModel({param_kwargs})
    result = await tool.arun(params)
    return result.model_dump()
"""
    namespace = {"InputModel": InputModel, "tool": tool}
    exec(code, namespace)
    mcp_tool_wrapper = namespace["mcp_tool_wrapper"]
    
    mcp_tool_wrapper.__name__ = tool_name
    mcp_tool_wrapper.__doc__ = tool_description

    if mcp is not None:
        mcp.tool(name=tool_name, description=tool_description)(mcp_tool_wrapper)

    return mcp_tool_wrapper
