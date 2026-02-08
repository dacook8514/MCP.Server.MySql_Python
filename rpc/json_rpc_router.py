"""JSON-RPC router.

Think of this as a tiny mediator + middleware pipeline:
- Find a handler by method name.
- Wrap it in behaviors (validation/logging/exception handling).
"""

import logging
from typing import Dict, List, Optional

from rpc.json_rpc_interfaces import (
    IJsonRpcHandler,
    IJsonRpcPipelineBehavior,
    JsonRpcError,
    JsonRpcRequest,
    JsonRpcResponse,
)

logger = logging.getLogger(__name__)


class JsonRpcRouter:
    def __init__(self, handlers: List[IJsonRpcHandler], behaviors: List[IJsonRpcPipelineBehavior]):
        # Dictionary lookup gives O(1) dispatch by method name.
        self._handlers: Dict[str, IJsonRpcHandler] = {
            handler.method_name: handler for handler in handlers
        }
        self._behaviors = behaviors

    async def handle_async(self, request: JsonRpcRequest) -> Optional[JsonRpcResponse]:
        # JSON-RPC notification: no response should be returned.
        if request.id is None:
            return None

        async def _execute_handler(req: JsonRpcRequest) -> JsonRpcResponse:
            handler = self._handlers.get(req.method)
            if not handler:
                return JsonRpcResponse(
                    id=req.id,
                    error=JsonRpcError(code=-32601, message=f"Method not found: {req.method}"),
                )
            return await handler.handle(req)

        # Compose middleware from inside-out (reverse order).
        pipeline = _execute_handler
        for behavior in reversed(self._behaviors):
            next_pipeline_step = pipeline
            pipeline = lambda req: behavior.handle(req, next_pipeline_step)

        try:
            return await pipeline(request)
        except Exception as exc:
            logger.exception("Unhandled exception during RPC request: %s", request.method)
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(code=-32000, message=f"Internal server error: {str(exc)}"),
            )
