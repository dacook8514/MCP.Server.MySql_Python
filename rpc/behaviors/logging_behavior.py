from rpc.json_rpc_interfaces import IJsonRpcPipelineBehavior, JsonRpcRequest, JsonRpcResponse
import logging

logger = logging.getLogger(__name__)

class JsonRpcLoggingBehavior(IJsonRpcPipelineBehavior):
    async def handle(
        self,
        request: JsonRpcRequest,
        next_behavior: callable
    ) -> JsonRpcResponse:
        logger.info(f"Incoming RPC request: Method='{request.method}', ID='{request.id}'")
        response = await next_behavior(request)
        logger.info(f"Outgoing RPC response for Method='{request.method}', ID='{request.id}': {response.dict()}")
        return response
