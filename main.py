from fastapi import FastAPI, Depends, HTTPException, status
from typing import List, Optional
import uvicorn
import logging

from config import DatabaseOptions
from database_service import DatabaseService
from models.table_schema import TableSchema

from rpc.json_rpc_interfaces import JsonRpcRequest, JsonRpcResponse, IJsonRpcHandler, IJsonRpcPipelineBehavior
from rpc.json_rpc_router import JsonRpcRouter
from rpc.handlers.ping_handler import PingHandler
from rpc.handlers.initialize_handler import InitializeHandler
from rpc.handlers.prompts_list_handler import PromptsListHandler
from rpc.behaviors.exception_behavior import JsonRpcExceptionBehavior
from rpc.behaviors.logging_behavior import JsonRpcLoggingBehavior
from rpc.behaviors.validation_behavior import JsonRpcValidationBehavior

from features.prompts.prompt_registry import PromptRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MCP.Server.MySql_Python", version="0.1.0")

# --- Configuration ---
# In a real application, this would be loaded from environment variables or a configuration file
# For now, using a placeholder connection string.
# IMPORTANT: Replace with your actual MySQL connection string.
db_options = DatabaseOptions(
    connection_string="server=localhost;port=3306;database=world;uid=api_user;pwd=StrongPasswordHere!;SslMode=Preferred;",
    command_timeout_seconds=60 # Example override
)

# --- Dependencies ---
def get_database_service() -> DatabaseService:
    return DatabaseService(db_options)

def get_prompt_registry() -> PromptRegistry:
    return PromptRegistry()

def get_json_rpc_router(
    prompt_registry: PromptRegistry = Depends(get_prompt_registry)
) -> JsonRpcRouter:
    # Register handlers
    handlers: List[IJsonRpcHandler] = [
        PingHandler(),
        InitializeHandler(),
        PromptsListHandler(prompt_registry)
        # Other handlers will be added here
    ]

    # Register pipeline behaviors
    behaviors: List[IJsonRpcPipelineBehavior] = [
        JsonRpcExceptionBehavior(),
        JsonRpcLoggingBehavior(),
        JsonRpcValidationBehavior()
    ]
    return JsonRpcRouter(handlers=handlers, behaviors=behaviors)

# --- HTTP Endpoints ---
@app.get("/api/mysql/health", summary="Simple health check endpoint.")
async def health():
    return "OK"

@app.get(
    "/api/mysql/schema",
    response_model=List[TableSchema],
    summary="Retrieves the database schema and exposes it as JSON."
)
async def get_schema(
    db_service: DatabaseService = Depends(get_database_service)
) -> List[TableSchema]:
    try:
        schema = await db_service.get_database_schema()
        return schema
    except Exception as e:
        logger.exception("Failed to retrieve database schema.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve database schema: {str(e)}"
        )

@app.post(
    "/mcp",
    response_model=Optional[JsonRpcResponse],
    summary="Entry point for all JSON-RPC requests from the client."
)
async def handle_rpc_request(
    request: JsonRpcRequest,
    router: JsonRpcRouter = Depends(get_json_rpc_router)
) -> Optional[JsonRpcResponse]:
    return await router.handle_async(request)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)