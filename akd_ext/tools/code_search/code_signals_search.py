"""
Code Signals Search Tool.

Searches LLM-extracted code signals from GitHub repositories.
Use as fallback when README-based search (RepositorySearchTool) is insufficient.
"""

import os
from typing import Any, Literal

import httpx
from loguru import logger
from pydantic import Field

from akd._base import InputSchema, OutputSchema
from akd.structures import SearchResult
from akd.tools import BaseTool, BaseToolConfig

from akd_ext.mcp import mcp_tool

DEFAULT_CODE_SIGNALS_BASE_URL = "https://dyejsbdumgpqz.cloudfront.net/"


class CodeSignalsSearchToolConfig(BaseToolConfig):
    """Configuration for the Code Signals Search Tool."""

    base_url: str = Field(
        default=os.getenv("SDE_CODE_SIGNALS_URL", DEFAULT_CODE_SIGNALS_BASE_URL),
        description="Base URL for the SDE Code Signals API",
    )
    timeout: float = Field(
        default=30.0,
        description="HTTP request timeout in seconds",
    )
    search_type: Literal["keyword"] = Field(
        default="keyword",
        description="Search type. Only 'keyword' is supported currently.",
    )


class CodeSignalsHit(SearchResult):
    """A single code signals hit from SDE search."""

    repo_id: str | None = Field(None, description="Repository identifier")
    repo_url: str | None = Field(None, description="GitHub repository URL")
    code_signals: str | None = Field(
        None,
        description="LLM-extracted signals: functions, classes, imports, data formats, summary",
    )


class CodeSignalsSearchInputSchema(InputSchema):
    """Input schema for Code Signals search."""

    query: str = Field(..., description="Search query for code functionality")
    limit: int = Field(default=5, ge=1, le=20, description="Maximum results to return")
    page: int = Field(default=1, ge=1, description="Page number for pagination")


class CodeSignalsSearchOutputSchema(OutputSchema):
    """Output schema for Code Signals search."""

    results: list[CodeSignalsHit] = Field(..., description="List of matching code signals")


@mcp_tool
class CodeSignalsSearchTool(BaseTool[CodeSignalsSearchInputSchema, CodeSignalsSearchOutputSchema]):
    """
    Search NASA code repositories using LLM-extracted code signals.

    Use this tool when README-based search is insufficient. Searches through
    extracted function names, class names, imports, data formats, and code summaries.
    """

    input_schema = CodeSignalsSearchInputSchema
    output_schema = CodeSignalsSearchOutputSchema
    config_schema = CodeSignalsSearchToolConfig

    def _parse_hit(self, doc: dict[str, Any], query: str) -> CodeSignalsHit:
        """Parse a single document from API response."""
        return CodeSignalsHit(
            query=query,
            title=doc.get("repo_id") or doc.get("name") or "Unknown",
            content=doc.get("code_signals") or "",
            score=doc.get("score") or doc.get("_score") or 0.0,
            repo_id=doc.get("repo_id"),
            repo_url=doc.get("repo_url"),
            code_signals=doc.get("code_signals"),
        )

    async def _arun(self, params: CodeSignalsSearchInputSchema) -> CodeSignalsSearchOutputSchema:
        """Execute Code Signals search."""
        request_body = {
            "search_term": params.query,
            "search_type": self.config.search_type,
            "pageSize": params.limit,
            "page": params.page,
        }

        logger.debug(f"Code Signals API request: {request_body}")

        url = f"{self.config.base_url.rstrip('/')}/api/code_signals/search"

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            try:
                response = await client.post(url, json=request_body)
                response.raise_for_status()
                data = response.json()
            except httpx.TimeoutException as e:
                msg = f"Code Signals API request timed out after {self.config.timeout}s"
                raise TimeoutError(msg) from e
            except httpx.HTTPStatusError as e:
                msg = f"Code Signals API returned error status {e.response.status_code}: {e.response.text}"
                raise RuntimeError(msg) from e
            except Exception as e:
                msg = f"Failed to query Code Signals API: {e}"
                raise RuntimeError(msg) from e

        if not data.get("success", False):
            msg = f"Code Signals API returned unsuccessful response: {data}"
            raise RuntimeError(msg)

        documents = [
            self._parse_hit(doc, params.query)
            for doc in data.get("documents", [])
        ]

        return CodeSignalsSearchOutputSchema(results=documents)
