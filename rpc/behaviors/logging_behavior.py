"""Pipeline behavior that logs requests/responses."""

import logging

from rpc.json_rpc_interfaces import IJsonRpcPipelineBehavior, JsonRpcRequest, JsonRpcResponse

logger = logging.getLogger(__name__)


class JsonRpcLoggingBehavior(IJsonRpcPipelineBehavior):
    async def handle(self, request: JsonRpcRequest, next_behavior: callable) -> JsonRpcResponse:
        logger.info("Incoming RPC request: Method='%s', ID='%s'", request.method, request.id)
        response = await next_behavior(request)
        logger.info(
            "Outgoing RPC response for Method='%s', ID='%s': %s",
            request.method,
            request.id,
            response.dict(),
        )
        return response
