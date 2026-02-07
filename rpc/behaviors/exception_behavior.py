from rpc.json_rpc_interfaces import IJsonRpcPipelineBehavior, JsonRpcRequest, JsonRpcResponse, JsonRpcError
import logging

logger = logging.getLogger(__name__)

class JsonRpcExceptionBehavior(IJsonRpcPipelineBehavior):
    async def handle(
        self,
        request: JsonRpcRequest,
        next_behavior: callable
    ) -> JsonRpcResponse:
        try:
            return await next_behavior(request)
        except Exception as e:
            logger.exception(f"Exception caught in RPC pipeline for method {request.method}: {e}")
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(code=-32000, message=f"Internal server error: {str(e)}")
            )
