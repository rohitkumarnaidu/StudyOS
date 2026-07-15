"""Typed MCP server entries parsed from configuration."""

from pydantic import BaseModel, Field


class MCPServerRecord(BaseModel):
    """One MCP peer — HTTP URL is supported today; command-based servers are reserved."""

    id: str = Field(min_length=1, max_length=64)
    url: str | None = Field(
        default=None,
        description="Base URL for JSON-RPC MCP (POST body).",
    )
    command: str | None = Field(
        default=None,
        description="Reserved for stdio MCP workers (not implemented in-process).",
    )
    args: list[str] = Field(default_factory=list)
