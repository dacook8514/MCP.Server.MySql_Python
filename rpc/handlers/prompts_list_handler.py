"""JSON-RPC handler that returns available prompt definitions."""

from typing import List

from features.prompts.prompt_registry import Prompt, PromptRegistry
from rpc.json_rpc_interfaces import IJsonRpcHandler, JsonRpcRequest, JsonRpcResponse


class PromptsListHandler(IJsonRpcHandler):
    def __init__(self, prompt_registry: PromptRegistry):
        self._prompt_registry = prompt_registry

    @property
    def method_name(self) -> str:
        return "prompts/list"

    async def handle(self, request: JsonRpcRequest) -> JsonRpcResponse:
        prompts: List[Prompt] = self._prompt_registry.get_prompts()
        # `p.dict()` is the Pydantic v1 way to serialize models to primitive dicts.
        return JsonRpcResponse(id=request.id, result=[prompt.dict() for prompt in prompts])
