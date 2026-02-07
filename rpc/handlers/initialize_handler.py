from rpc.json_rpc_interfaces import IJsonRpcHandler, JsonRpcRequest, JsonRpcResponse
from pydantic import BaseModel
from typing import Dict, Any

class InitializeResult(BaseModel):
    message: str
    capabilities: Dict[str, Any] = {}

class InitializeHandler(IJsonRpcHandler):
    @property
    def method_name(self) -> str:
        return "initialize"

    async def handle(self, request: JsonRpcRequest) -> JsonRpcResponse:
        # The 'params' of an initialize request typically contain client capabilities.
        # For this example, we'll just acknowledge the initialization.
        return JsonRpcResponse(
            id=request.id,
            result=InitializeResult(
                message="Initialized",
                capabilities={"supports_ping": True, "supports_schema_retrieval": True}
            )
        )
