import pytest
from akd_ext.tools.reverse import ReverseTool, ReverseToolInputSchema
from akd_ext.mcp.converter import toolConverter

class TestReverseTool:
    @pytest.mark.asyncio
    async def test_reverse_simple(self):
        tool = ReverseTool()
        result = await tool.arun(ReverseToolInputSchema(text="hello"))
        assert result.reversed_text == "olleh"

    @pytest.mark.asyncio
    async def test_reverse_sentence(self):
        tool = ReverseTool()
        result = await tool.arun(ReverseToolInputSchema(text="NASA IMPACT"))
        assert result.reversed_text == "TCAPMI ASAN"

class TestToolConverter:
    def test_converter_returns_callable(self):
        tool = ReverseTool()
        mcp_tool = toolConverter(tool)
        assert callable(mcp_tool)

    @pytest.mark.asyncio
    async def test_converted_tool_works(self):
        tool = ReverseTool()
        mcp_tool = toolConverter(tool)
        result = await mcp_tool(text="test")
        assert result["reversed_text"] == "tset"
