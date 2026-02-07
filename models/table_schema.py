from typing import List
from pydantic import BaseModel, Field
from .column_schema import ColumnSchema
from .foreign_key_schema import ForeignKeySchema

class TableSchema(BaseModel):
    name: str = Field(..., description="The name of the table.")
    columns: List[ColumnSchema] = Field(default_factory=list, description="List of columns in the table.")
    primary_key_columns: List[str] = Field(default_factory=list, description="List of column names forming the primary key.")
    foreign_keys: List[ForeignKeySchema] = Field(default_factory=list, description="List of foreign key constraints.")
