"""JSON-RPC contracts.

This file mixes:
1) Data contracts (Pydantic models, similar to DTOs), and
2) Interface-like abstractions (Python ABCs, similar to C# interfaces/abstract classes).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


# --- JSON-RPC Models ----------------------------------------------------------
class JsonRpcError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    # JSON-RPC params can be positional (list) or named (object/dict).
    params: Optional[Union[List[Any], Dict[str, Any]]] = None
    # `id=None` represents a notification (fire-and-forget).
    id: Optional[Union[int, str]] = None


class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[JsonRpcError] = None
    id: Optional[Union[int, str]] = None


# --- JSON-RPC Interfaces ------------------------------------------------------
class IJsonRpcHandler(ABC):
    """Handler contract for one RPC method."""

    @property
    @abstractmethod
    def method_name(self) -> str:
        """Return the method name this handler supports."""

    @abstractmethod
    async def handle(self, request: JsonRpcRequest) -> JsonRpcResponse:
        """Process one JSON-RPC request and return a response."""


class IJsonRpcPipelineBehavior(ABC):
    """Middleware contract for cross-cutting behavior around handlers."""

    @abstractmethod
    async def handle(self, request: JsonRpcRequest, next_behavior: callable) -> JsonRpcResponse:
        """Invoke current behavior and then (optionally) call the next step."""
