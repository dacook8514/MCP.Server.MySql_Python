"""In-memory prompt catalog used by the prompts/list RPC method."""

from typing import Dict, List, Optional

from pydantic import BaseModel


class Prompt(BaseModel):
    """Prompt metadata + template text."""

    name: str
    description: str
    template: str


class PromptRegistry:
    """Stores prompts in a dictionary keyed by prompt name."""

    def __init__(self):
        self._prompts: Dict[str, Prompt] = {}
        self.add_prompt(
            Prompt(
                name="example_prompt",
                description="An example prompt.",
                template="SELECT * FROM {table_name} LIMIT {limit};",
            )
        )

    def add_prompt(self, prompt: Prompt) -> None:
        self._prompts[prompt.name] = prompt

    def get_prompts(self) -> List[Prompt]:
        # `dict.values()` returns a view; `list(...)` materializes it.
        return list(self._prompts.values())

    def get_prompt(self, name: str) -> Optional[Prompt]:
        return self._prompts.get(name)
