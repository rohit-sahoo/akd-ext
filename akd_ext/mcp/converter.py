from typing import Callable, get_type_hints
from inspect import Signature, Parameter
from fastmcp import FastMCP
from akd.tools._base import BaseTool


def toolConverter(tool: BaseTool, mcp: FastMCP | None = None) -> Callable:
    """Convert akd BaseTool to FastMCP tool."""
    tool_name = tool.name or tool.__class__.__name__
    tool_description = tool.description or ""
    InputModel = tool.input_schema

    # Build signature from InputModel fields
    field_info = InputModel.model_fields
    parameters = []
    annotations = {}
    
    for field_name, field in field_info.items():
        field_type = field.annotation
        annotations[field_name] = field_type
        
        # Create parameter with proper default
        if field.default is not ...:
            param = Parameter(
                field_name,
                Parameter.POSITIONAL_OR_KEYWORD,
                default=field.default,
                annotation=field_type
            )
        else:
            param = Parameter(
                field_name,
                Parameter.POSITIONAL_OR_KEYWORD,
                annotation=field_type
            )
        parameters.append(param)
    
    # Create signature object
    wrapper_sig = Signature(parameters)
    
    # Create closure that captures InputModel and tool
    def _create_wrapper():
        async def _async_wrapper(*args, **kwargs):
            # Bind arguments to signature
            bound = wrapper_sig.bind(*args, **kwargs)
            bound.apply_defaults()
            # Create InputModel instance
            params = InputModel(**bound.arguments)
            # Run tool and return result
            result = await tool.arun(params)
            return result.model_dump()
        
        return _async_wrapper
    
    mcp_tool_wrapper = _create_wrapper()
    
    # Set function metadata
    mcp_tool_wrapper.__name__ = tool_name
    mcp_tool_wrapper.__doc__ = tool_description
    mcp_tool_wrapper.__signature__ = wrapper_sig
    mcp_tool_wrapper.__annotations__ = annotations

    if mcp is not None:
        mcp.tool(name=tool_name, description=tool_description)(mcp_tool_wrapper)

    return mcp_tool_wrapper
