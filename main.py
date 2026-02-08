"""Application entry point.

Notes for C# developers:
- FastAPI's dependency injection is function-based (`Depends(...)`) rather than attribute-based.
- `async def` endpoints are like `Task<T>` actions in ASP.NET Core.
- Module-level code (outside functions/classes) runs at import time.
"""

import logging
import os
from typing import List, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status

from config import DatabaseOptions
from database_service import DatabaseService
from features.prompts.prompt_registry import PromptRegistry
from models.table_schema import TableSchema
from rpc.behaviors.exception_behavior import JsonRpcExceptionBehavior
from rpc.behaviors.logging_behavior import JsonRpcLoggingBehavior
from rpc.behaviors.validation_behavior import JsonRpcValidationBehavior
from rpc.handlers.initialize_handler import InitializeHandler
from rpc.handlers.ping_handler import PingHandler
from rpc.handlers.prompts_list_handler import PromptsListHandler
from rpc.json_rpc_interfaces import (
    IJsonRpcHandler,
    IJsonRpcPipelineBehavior,
    JsonRpcRequest,
    JsonRpcResponse,
)
from rpc.json_rpc_router import JsonRpcRouter

# Similar to configuring logging providers in Program.cs.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app instance (roughly equivalent to WebApplication in ASP.NET Core).
app = FastAPI(title="MCP.Server.MySql_Python", version="0.1.0")

# Read environment variable once at startup.
# If this is missing, DB calls will fail later when a connection is attempted.
db_connection_string = os.getenv("DB_CONNECTION_STRING")

# Pydantic model used as strongly-typed options (think IOptions<T> payload).
db_options = DatabaseOptions(
    connection_string=db_connection_string,
    command_timeout_seconds=60,
)


# --- Dependencies -------------------------------------------------------------
# In FastAPI, DI is usually expressed as simple functions.
def get_database_service() -> DatabaseService:
    """Return a service instance for each request."""
    return DatabaseService(db_options)


def get_prompt_registry() -> PromptRegistry:
    """Return the prompt registry dependency."""
    return PromptRegistry()


def get_json_rpc_router(
    prompt_registry: PromptRegistry = Depends(get_prompt_registry),
) -> JsonRpcRouter:
    """Compose handlers + behaviors and return a configured router."""
    handlers: List[IJsonRpcHandler] = [
        PingHandler(),
        InitializeHandler(),
        PromptsListHandler(prompt_registry),
    ]

    # Behaviors are middleware-like decorators around the final handler.
    behaviors: List[IJsonRpcPipelineBehavior] = [
        JsonRpcExceptionBehavior(),
        JsonRpcLoggingBehavior(),
        JsonRpcValidationBehavior(),
    ]
    return JsonRpcRouter(handlers=handlers, behaviors=behaviors)


# --- HTTP Endpoints -----------------------------------------------------------
@app.get("/api/mysql/health", summary="Simple health check endpoint.")
async def health() -> str:
    """Minimal endpoint used for liveness checks."""
    return "OK"


@app.get(
    "/api/mysql/schema",
    response_model=List[TableSchema],
    summary="Retrieves the database schema and exposes it as JSON.",
)
async def get_schema(
    db_service: DatabaseService = Depends(get_database_service),
) -> List[TableSchema]:
    """Return table metadata from MySQL."""
    try:
        return await db_service.get_database_schema()
    except Exception as exc:
        # FastAPI raises HTTPException to produce a specific HTTP status code.
        logger.exception("Failed to retrieve database schema.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve database schema: {str(exc)}",
        )


@app.post(
    "/mcp",
    response_model=Optional[JsonRpcResponse],
    summary="Entry point for all JSON-RPC requests from the client.",
)
async def handle_rpc_request(
    request: JsonRpcRequest,
    router: JsonRpcRouter = Depends(get_json_rpc_router),
) -> Optional[JsonRpcResponse]:
    """Delegate JSON-RPC request routing to the router component."""
    return await router.handle_async(request)


if __name__ == "__main__":
    # Equivalent idea to `dotnet run`: start the ASGI server.
    uvicorn.run(app, host="0.0.0.0", port=8000)
