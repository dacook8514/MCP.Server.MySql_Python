from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class QueryResult(BaseModel):
    columns: List[str] = Field(default_factory=list, description="List of column names returned by the query.")
    rows: List[Dict[str, Any]] = Field(default_factory=list, description="List of rows, where each row is a dictionary mapping column names to their values.")
    records_affected: int = Field(0, description="The number of records affected by the query.")
