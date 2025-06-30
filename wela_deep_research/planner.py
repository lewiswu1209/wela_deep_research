
import time
import json
import logging

from wela_agents.models.openai_chat import OpenAIChat
from wela_agents.schema.template.openai_chat import ChatTemplate
from wela_agents.schema.template.openai_chat import SystemMessageTemplate
from wela_agents.schema.template.prompt_template import StringPromptTemplate

from wela_deep_research.state import ReportState
from wela_deep_research.prompt import report_planner_instructions
from wela_deep_research.adapter import Adapter

class Planner(Adapter):

    def __init__(self, *, model: OpenAIChat, state: ReportState, input_key: str, output_key: str):
        super().__init__(
            model=model,
            prompt_template=ChatTemplate(
                [
                    SystemMessageTemplate(
                        StringPromptTemplate(report_planner_instructions)
                    )
                ]
            ),
            state=state,
            input_key=input_key,
            output_key=output_key
        )

    def predict(self, **kwargs):
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
