"""Result object for SQL execution."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class QueryResult(BaseModel):
    columns: List[str] = Field(
        default_factory=list,
        description="List of column names returned by the query.",
    )
    rows: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Rows represented as dictionaries keyed by column name.",
    )
    records_affected: int = Field(
        0,
        description="The number of records affected by the query.",
    )
