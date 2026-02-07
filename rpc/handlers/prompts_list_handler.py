from rpc.json_rpc_interfaces import IJsonRpcHandler, JsonRpcRequest, JsonRpcResponse
from features.prompts.prompt_registry import PromptRegistry, Prompt
from typing import List

class PromptsListHandler(IJsonRpcHandler):
    def __init__(self, prompt_registry: PromptRegistry):
        self._prompt_registry = prompt_registry

    @property
    def method_name(self) -> str:
        return "prompts/list"

    async def handle(self, request: JsonRpcRequest) -> JsonRpcResponse:
        prompts: List[Prompt] = self._prompt_registry.get_prompts()
        return JsonRpcResponse(id=request.id, result=[p.dict() for p in prompts])
