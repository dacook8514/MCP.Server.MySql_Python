"""Database access layer.

Teaching notes (for C# developers):
- `async with` is similar to `await using` in C# for async disposable resources.
- List/dict comprehensions are concise equivalents of simple LINQ projections.
- Python relies on duck typing: we annotate for clarity, but runtime does not enforce
  these types unless a library (like Pydantic) validates data.
"""

from typing import Any, Dict, List

import aiomysql.cursors

from config import DatabaseOptions
from models.column_schema import ColumnSchema
from models.foreign_key_schema import ForeignKeyColumn, ForeignKeySchema
from models.query_result import QueryResult
from models.table_schema import TableSchema


class DatabaseService:
    """Provides async MySQL operations used by API/RPC endpoints."""

    def __init__(self, options: DatabaseOptions):
        self.options = options

    async def get_database_schema(self) -> List[TableSchema]:
        """Read table/column/key metadata from INFORMATION_SCHEMA."""
        tables: Dict[str, TableSchema] = {}

        connection = await self._get_connection()
        try:
            async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
                # First query: table columns.
                await cursor.execute(
                    """
                    SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                    """
                )

                for row in await cursor.fetchall():
                    table_name = row["TABLE_NAME"]
                    column = ColumnSchema(
                        name=row["COLUMN_NAME"],
                        data_type=row["DATA_TYPE"],
                        is_nullable=row["IS_NULLABLE"] == "YES",
                    )

                    # Equivalent to `TryGetValue` + initialize in C#.
                    if table_name not in tables:
                        tables[table_name] = TableSchema(name=table_name)
                    tables[table_name].columns.append(column)

                # Second query: PK/FK constraints.
                await cursor.execute(
                    """
                    SELECT tc.TABLE_NAME,
                           tc.CONSTRAINT_TYPE,
                           kcu.CONSTRAINT_NAME,
                           kcu.COLUMN_NAME,
                           kcu.REFERENCED_TABLE_NAME,
                           kcu.REFERENCED_COLUMN_NAME
                    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                            ON tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
                                   AND tc.TABLE_NAME = kcu.TABLE_NAME
                                   AND tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                    WHERE tc.TABLE_SCHEMA = DATABASE()
                      AND tc.CONSTRAINT_TYPE IN ('PRIMARY KEY', 'FOREIGN KEY')
                    ORDER BY tc.TABLE_NAME, kcu.ORDINAL_POSITION
                    """
                )

                for row in await cursor.fetchall():
                    table_name = row["TABLE_NAME"]
                    constraint_type = row["CONSTRAINT_TYPE"]
                    constraint_name = row["CONSTRAINT_NAME"]
                    column_name = row["COLUMN_NAME"]
                    referenced_table = row["REFERENCED_TABLE_NAME"] or ""
                    referenced_column = row["REFERENCED_COLUMN_NAME"] or ""

                    if table_name not in tables:
                        tables[table_name] = TableSchema(name=table_name)

                    table = tables[table_name]

                    # `next(generator, default)` is a common Python lookup idiom.
                    column = next((c for c in table.columns if c.name == column_name), None)

                    if constraint_type == "PRIMARY KEY":
                        if column_name not in table.primary_key_columns:
                            table.primary_key_columns.append(column_name)
                        if column:
                            column.is_primary_key = True
                    elif constraint_type == "FOREIGN KEY":
                        if column:
                            column.is_foreign_key = True

                        foreign_key = next(
                            (fk for fk in table.foreign_keys if fk.name == constraint_name),
                            None,
                        )
                        if foreign_key is None:
                            foreign_key = ForeignKeySchema(
                                name=constraint_name,
                                referenced_table=referenced_table,
                            )
                            table.foreign_keys.append(foreign_key)

                        foreign_key.columns.append(
                            ForeignKeyColumn(
                                column=column_name,
                                referenced_column=referenced_column,
                            )
                        )
        finally:
            # aiomysql connections are closed explicitly.
            connection.close()

        return list(tables.values())

    async def execute_query(self, query: str) -> QueryResult:
        """Execute SQL and return tabular results."""
        connection = await self._get_connection()
        try:
            async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
                if self.options.command_timeout_seconds > 0:
                    # MySQL timeout is configured in milliseconds.
                    await cursor.execute(
                        f"SET SESSION MAX_EXECUTION_TIME = {self.options.command_timeout_seconds * 1000}"
                    )

                # TODO: enforce_read_only / require_limit safety checks.
                await cursor.execute(query)

                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = await cursor.fetchall()
                records_affected = cursor.rowcount

                # DictCursor rows are already dictionaries.
                formatted_rows = [
                    {key: (None if value is None else value) for key, value in row.items()}
                    for row in rows
                ]
        finally:
            connection.close()

        return QueryResult(
            columns=columns,
            rows=formatted_rows,
            records_affected=records_affected,
        )

    async def _get_connection(self):
        """Create an aiomysql connection from a semicolon-delimited connection string."""
        # Example input: "server=localhost;database=test;uid=root;pwd=secret"
        parts = {
            piece.split("=", 1)[0].strip().lower(): piece.split("=", 1)[1].strip()
            for piece in self.options.connection_string.split(";")
            if piece
        }

        return await aiomysql.connect(
            host=parts.get("server") or parts.get("host", "localhost"),
            user=parts.get("uid") or parts.get("user", "root"),
            password=parts.get("pwd") or parts.get("password", ""),
            db=parts.get("database") or parts.get("db"),
            charset="utf8mb4",
            cursorclass=aiomysql.cursors.Cursor,
            autocommit=True,
        )
