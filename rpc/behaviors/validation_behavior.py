from rpc.json_rpc_interfaces import IJsonRpcPipelineBehavior, JsonRpcRequest, JsonRpcResponse, JsonRpcError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class JsonRpcValidationBehavior(IJsonRpcPipelineBehavior):
    async def handle(
        self,
        request: JsonRpcRequest,
        next_behavior: callable
    ) -> JsonRpcResponse:
        try:
            # Pydantic validation already happens when JsonRpcRequest is instantiated
            # We can add more specific validation logic here if needed, e.g.,
            # checking if method name is valid, params type, etc.
            if request.jsonrpc != "2.0":
                return JsonRpcResponse(
                    id=request.id,
                    error=JsonRpcError(code=-32600, message="Invalid Request: jsonrpc must be '2.0'")
                )
            
            # Additional validation: method must be a string
            if not isinstance(request.method, str):
                return JsonRpcResponse(
                    id=request.id,
                    error=JsonRpcError(code=-32600, message="Invalid Request: method must be a string")
                )

            return await next_behavior(request)
        except ValidationError as e:
            logger.warning(f"JSON RPC Request validation failed: {e.errors()}")
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(code=-32700, message="Parse error: Invalid JSON RPC request format", data=e.errors())
            )
        except Exception as e:
            logger.exception(f"Unexpected error during RPC request validation: {request.method}")
            return JsonRpcResponse(
                id=request.id,
                error=JsonRpcError(code=-32000, message=f"Internal server error during validation: {str(e)}")
            )
