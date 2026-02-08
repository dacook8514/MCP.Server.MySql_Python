"""Configuration models.

Pydantic `BaseModel` gives us runtime validation + type coercion,
which is conceptually similar to binding configuration to a C# options class.
"""

from pydantic import BaseModel, Field


class DatabaseOptions(BaseModel):
    """Connection and query-safety options for MySQL access."""

    # `Field(...)` means "required". If omitted, Pydantic raises a validation error.
    connection_string: str = Field(
        ...,
        description="Connection string used to connect to the database.",
    )
    enforce_read_only: bool = Field(
        True,
        description="Enforces read-only queries (SELECT/CTE only).",
    )
    require_limit: bool = Field(
        True,
        description="Requires a LIMIT clause and appends one if missing.",
    )
    max_rows: int = Field(
        500,
        description="Maximum rows to return when a LIMIT is required.",
    )
    command_timeout_seconds: int = Field(
        30,
        description="Command timeout in seconds.",
    )
