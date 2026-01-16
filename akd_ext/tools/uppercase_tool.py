from pydantic import Field
from akd._base import InputSchema, OutputSchema
from akd.tools._base import BaseTool
from akd_ext.mcp.decorators import mcp_tool


class UppercaseToolInputSchema(InputSchema):
    """Input schema for UppercaseTool."""
    text: str = Field(..., description="Text to convert to uppercase")


class UppercaseToolOutputSchema(OutputSchema):
    """Output schema for UppercaseTool."""
    uppercase_text: str = Field(..., description="Text converted to uppercase")


@mcp_tool
class UppercaseTool(BaseTool):
    """Converts text to uppercase."""
    
    name = "uppercase_tool"
    description = "Converts text to uppercase"
    input_schema = UppercaseToolInputSchema
    output_schema = UppercaseToolOutputSchema
    
    async def _arun(self, params: UppercaseToolInputSchema, **kwargs) -> UppercaseToolOutputSchema:
        return UppercaseToolOutputSchema(uppercase_text=params.text.upper())
