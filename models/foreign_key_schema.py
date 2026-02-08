"""Pydantic models for foreign key metadata."""

from typing import List

from pydantic import BaseModel, Field


class ForeignKeyColumn(BaseModel):
    column: str = Field(..., description="The name of the column in the referencing table.")
    referenced_column: str = Field(
        ...,
        description="The name of the referenced column in the foreign table.",
    )


class ForeignKeySchema(BaseModel):
    name: str = Field(..., description="The name of the foreign key constraint.")
    referenced_table: str = Field(..., description="The name of the table being referenced.")
    columns: List[ForeignKeyColumn] = Field(
        default_factory=list,
        description="List of columns forming the foreign key.",
    )
