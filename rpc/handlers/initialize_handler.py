"""Implementation of the JSON-RPC `initialize` method."""

from typing import Any, Dict

from pydantic import BaseModel

from rpc.json_rpc_interfaces import IJsonRpcHandler, JsonRpcRequest, JsonRpcResponse


class InitializeResult(BaseModel):
    """Structured payload returned to the client on initialization."""

    message: str
    # In Python, default mutable values should be created carefully.
    # Here it is safe because this object is short-lived, but in general prefer default_factory.
    capabilities: Dict[str, Any] = {}


class InitializeHandler(IJsonRpcHandler):
    @property
    def method_name(self) -> str:
        return "initialize"

    async def handle(self, request: JsonRpcRequest) -> JsonRpcResponse:
        # In real systems, you may inspect request.params and negotiate capabilities.
        return JsonRpcResponse(
            id=request.id,
            result=InitializeResult(
                message="Initialized",
                capabilities={"supports_ping": True, "supports_schema_retrieval": True},
            ),
        )
