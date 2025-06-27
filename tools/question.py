
from typing import Any
from typing import Callable

from wela_agents.toolkit.toolkit import Tool

class Question(Tool):
    def __init__(self) -> None:
        super().__init__(
            name="question_tool",
            description="Ask a follow-up question to clarify the report scope.",
            required=["question"],
            question={
                "type": "string",
                "description": "A specific question to ask the user to clarify the scope, focus, or requirements of the report."
            }
        )

    def _invoke(self, callback: Callable = None, **kwargs: Any) -> str:
        question = kwargs["question"]
        print(f"I need ask the question '{question}'")
        return f"You need ask the question '{question}'"

__all__ = [
    "Question"
]
