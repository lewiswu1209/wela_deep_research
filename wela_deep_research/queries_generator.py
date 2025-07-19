
import time
import json
import logging

from typing import Any
from typing import Union
from typing import Generator
from wela_agents.models.openai_chat import OpenAIChat
from wela_agents.schema.template.openai_chat import ChatTemplate
from wela_agents.schema.template.openai_chat import UserMessageTemplate
from wela_agents.schema.template.prompt_template import StringPromptTemplate

from .state import ReportState
from .prompt import queries_generator_instructions
from .adapter import Adapter

class QueriesGenerator(Adapter):

    def __init__(self, *, model: OpenAIChat, state: ReportState, input_key: str, output_key: str) -> None:
        super().__init__(
            model=model,
            prompt_template=ChatTemplate(
                [
                    UserMessageTemplate(
                        StringPromptTemplate(queries_generator_instructions)
                    )
                ]
            ),
            state=state,
            input_key=input_key,
            output_key=output_key
        )

    def predict(self, **kwargs: Any) -> Union[Any, Generator[Any, None, None]]:
        self.state["topic"] = kwargs["topic"]
        section = self.state["sections"][self.state["current_section_index"]]
        if section["Research"]:
            logging.info(f"Generating queries for section: '{section["Name"]}'")

            kwargs["section_description"] = section["Description"]
            kwargs["number_of_queries"] = 3
            kwargs["today"]=time.strftime("%Y-%m-%d")
            response = super().predict(**kwargs)["content"]
            self.state["queries_list"] = json.loads(response.lstrip("```json").rstrip("```"))

            logging.info(
f'''> Generated queries for section '{section["Name"]}':
{"\n".join(self.state["queries_list"])}
'''
            )
        else:
              self.state["queries_list"] = []
