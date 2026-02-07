from rpc.json_rpc_interfaces import IJsonRpcHandler, JsonRpcRequest, JsonRpcResponse

class PingHandler(IJsonRpcHandler):
    @property
    def method_name(self) -> str:
        return "ping"

    async def handle(self, request: JsonRpcRequest) -> JsonRpcResponse:
        return JsonRpcResponse(id=request.id, result="Pong!")
