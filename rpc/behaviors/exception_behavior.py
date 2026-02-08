"""Pipeline behavior that converts unhandled exceptions to JSON-RPC errors."""

import logging

from rpc.json_rpc_interfaces import (
    IJsonRpcPipelineBehavior,
    JsonRpcError,
    JsonRpcRequest,
    JsonRpcResponse,
)

logger = logging.getLogger(__name__)


class JsonRpcExceptionBehavior(IJsonRpcPipelineBehavior):
    async def handle(self, request: JsonRpcRequest, next_behavior: callable) -> JsonRpcResponse:
        try:
            return await next_behavior(request)
        except Exception as exc:
            logger.exception(
                "Exception caught in RPC pipeline for method %s: %s",
                request.method,
                exc,
            )
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(code=-32000, message=f"Internal server error: {str(exc)}"),
            )
