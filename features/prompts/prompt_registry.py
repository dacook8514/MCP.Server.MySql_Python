from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class Prompt(BaseModel):
    name: str
    description: str
    template: str

class PromptRegistry:
    def __init__(self):
        self._prompts: Dict[str, Prompt] = {}
        # Example prompt
        self.add_prompt(Prompt(
            name="example_prompt",
            description="An example prompt.",
            template="SELECT * FROM {table_name} LIMIT {limit};"
        ))

    def add_prompt(self, prompt: Prompt):
        self._prompts[prompt.name] = prompt

    def get_prompts(self) -> List[Prompt]:
        return list(self._prompts.values())

    def get_prompt(self, name: str) -> Optional[Prompt]:
        return self._prompts.get(name)
