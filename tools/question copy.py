
from typing import Any
from typing import Callable

from wela_agents.toolkit.toolkit import Tool

class Sections(Tool):
    def __init__(self) -> None:
        super().__init__(
            name="sections_tool",
            description="List of section titles of the report.",
            required=["sections"],
            sections={
                "type": "string",
                "description": "Sections of the report."
            }
        )

    def _invoke(self, callback: Callable = None, **kwargs: Any) -> str:
        question = kwargs["question"]
        print(f"I need ask the question '{question}'")
        return f"You need ask the question '{question}'"

__all__ = [
    "Sections"
]
