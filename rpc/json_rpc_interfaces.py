from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

# --- JSON RPC Models ---
class JsonRpcError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Union[List[Any], Dict[str, Any]]] = None
    id: Optional[Union[int, str]] = None

class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[JsonRpcError] = None
    id: Optional[Union[int, str]] = None

# --- JSON RPC Interfaces ---
class IJsonRpcHandler(ABC):
    """
    Abstract base class for JSON RPC handlers.
    Each handler is responsible for a specific RPC method.
    """
    @property
    @abstractmethod
    def method_name(self) -> str:
        """The name of the RPC method this handler processes."""
        pass

    @abstractmethod
    async def handle(self, request: JsonRpcRequest) -> JsonRpcResponse:
        """Handles the incoming JSON RPC request."""
        pass

class IJsonRpcPipelineBehavior(ABC):
    """
    Abstract base class for JSON RPC pipeline behaviors (middleware).
    Behaviors can intercept and process requests/responses in the pipeline.
    """
    @abstractmethod
    async def handle(
        self,
        request: JsonRpcRequest,
        next_behavior: callable
    ) -> JsonRpcResponse:
        """
        Handles the request in the pipeline.
        
        Args:
            request: The incoming JsonRpcRequest.
            next_behavior: A callable that invokes the next behavior in the pipeline
                           or the final handler.
        Returns:
            The JsonRpcResponse after processing.
        """
        pass
