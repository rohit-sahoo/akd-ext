from pydantic import Field
from akd._base import InputSchema, OutputSchema
from akd.tools._base import BaseTool
from akd_ext.mcp.decorators import mcp_tool


class ReverseToolInputSchema(InputSchema):
    """Input schema for ReverseTool."""
    text: str = Field(..., description="Text to reverse")


class ReverseToolOutputSchema(OutputSchema):
    """Output schema for ReverseTool."""
    reversed_text: str = Field(..., description="Reversed text")


@mcp_tool
class ReverseTool(BaseTool):
    """Reverses input text."""
    
    name = "reverse_tool"
    description = "Reverses the input text"
    input_schema = ReverseToolInputSchema
    output_schema = ReverseToolOutputSchema
    
    async def _arun(self, params: ReverseToolInputSchema, **kwargs) -> ReverseToolOutputSchema:
        return ReverseToolOutputSchema(reversed_text=params.text[::-1])
