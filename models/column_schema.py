from pydantic import BaseModel, Field

class ColumnSchema(BaseModel):
    name: str = Field(..., description="The name of the column.")
    data_type: str = Field(..., description="The data type of the column.")
    is_nullable: bool = Field(..., description="True if the column can contain NULL values, False otherwise.")
    is_primary_key: bool = Field(False, description="True if the column is part of the primary key.")
    is_foreign_key: bool = Field(False, description="True if the column is part of a foreign key.")
