
import re

from typing import Any
from typing import Union
from typing import Generator
from wela_agents.agents.llm import LLMAgent
from wela_agents.agents.workflow import StatefulAgent
from wela_agents.models.openai_chat import OpenAIChat
from wela_agents.schema.template.prompt_template import PromptTemplate

from .state import ReportState

class Adapter(StatefulAgent):

    def __init__(
            self,
            *,
            model: OpenAIChat,
            prompt_template: PromptTemplate,
            state: ReportState,
            input_key: str,
            output_key: str
        ) -> None:
        self.__agent = LLMAgent(model=model, prompt_template=prompt_template)
        super().__init__(state=state, input_key=input_key, output_key=output_key)

    def predict(self, **kwargs: Any) -> Union[Any, Generator[Any, None, None]]:
        response = self.__agent.predict(**kwargs)
        match = re.search(r'(?:<think>)?.*?</think>(.*)', response["content"], re.DOTALL)
        if match:
            response["content"] = match.group(1).strip()
        return response
