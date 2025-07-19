
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
from .prompt import report_planner_instructions
from .adapter import Adapter

class Planner(Adapter):

    def __init__(self, *, model: OpenAIChat, state: ReportState, input_key: str, output_key: str) -> None:
        super().__init__(
            model=model,
            prompt_template=ChatTemplate(
                [
                    UserMessageTemplate(
                        StringPromptTemplate(report_planner_instructions)
                    )
                ]
            ),
            state=state,
            input_key=input_key,
            output_key=output_key
        )

    def predict(self, **kwargs: Any) -> Union[Any, Generator[Any, None, None]]:
        self.state["topic"] = kwargs["topic"]

        logging.info(f"> Planning report structure, the topic is: '{self.state["topic"]}'")

        kwargs["today"]=time.strftime("%Y-%m-%d")
        response = super().predict(**kwargs)["content"]
        self.state["sections"] = json.loads(response.lstrip("```json").rstrip("```"))
        self.state["current_section_index"] = 1

        logging_str = "> Generated report structure:\n"
        for section in self.state["sections"]:
            logging_str += f"""
 - Section: {section["Name"]}
 - Description: {section["Description"]}
 - Research: {section["Research"]}
 - Content: {section.get("Content") if section.get("Content", None) else '[Not yet written]'}
"""
        logging.info(logging_str)
