"""Pipeline behavior for protocol-level validation."""

import logging

from pydantic import ValidationError

from rpc.json_rpc_interfaces import (
    IJsonRpcPipelineBehavior,
    JsonRpcError,
    JsonRpcRequest,
    JsonRpcResponse,
)

logger = logging.getLogger(__name__)


class JsonRpcValidationBehavior(IJsonRpcPipelineBehavior):
    async def handle(self, request: JsonRpcRequest, next_behavior: callable) -> JsonRpcResponse:
        try:
            # Most structural validation already happened when Pydantic created the model.
            if request.jsonrpc != "2.0":
                return JsonRpcResponse(
                    id=request.id,
                    error=JsonRpcError(
                        code=-32600,
                        message="Invalid Request: jsonrpc must be '2.0'",
                    ),
                )

            if not isinstance(request.method, str):
                return JsonRpcResponse(
                    id=request.id,
                    error=JsonRpcError(
                        code=-32600,
                        message="Invalid Request: method must be a string",
                    ),
                )

            return await next_behavior(request)
        except ValidationError as exc:
            logger.warning("JSON RPC Request validation failed: %s", exc.errors())
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=-32700,
                    message="Parse error: Invalid JSON RPC request format",
                    data=exc.errors(),
                ),
            )
        except Exception as exc:
            logger.exception("Unexpected error during RPC request validation: %s", request.method)
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(
                    code=-32000,
                    message=f"Internal server error during validation: {str(exc)}",
                ),
            )
