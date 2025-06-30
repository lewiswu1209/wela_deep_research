
import json
import logging

from wela_agents.models.openai_chat import OpenAIChat
from wela_agents.schema.template.openai_chat import ChatTemplate
from wela_agents.schema.template.openai_chat import UserMessageTemplate
from wela_agents.schema.template.openai_chat import SystemMessageTemplate
from wela_agents.schema.template.prompt_template import StringPromptTemplate

from wela_deep_research.state import ReportState
from wela_deep_research.prompt import section_grader_instructions
from wela_deep_research.adapter import Adapter

class Grader(Adapter):

    def __init__(self, *, model: OpenAIChat, state: ReportState, input_key: str, output_key: str):
        super().__init__(
            model=model,
            prompt_template=ChatTemplate(
                [
                    SystemMessageTemplate(
                        StringPromptTemplate(section_grader_instructions)
                    ),
                    UserMessageTemplate(
                        StringPromptTemplate(
                            """Grade the report and consider follow-up questions for missing information.
If the grade is 'pass', return empty strings for all follow-up keywords.
If the grade is 'fail', provide specific search keywords to gather missing information."""
                        )
                    )
                ]
            ),
            state=state,
            input_key=input_key,
            output_key=output_key
        )

    def predict(self, **kwargs):
        section = self.state["sections"][self.state["current_section_index"]]

        logging.info(f"> Grading section: '{section["Name"]}'")

        kwargs["section_description"] = section["Description"]
        kwargs["section_content"] = section.get("Content", "[Not written yet]")
        kwargs["number_of_follow_up_queries"] = 3
        response = super().predict(**kwargs)["content"]
        grade = json.loads(response.lstrip("```json").rstrip("```"))
        logging.info(f"> Graded section '{section["Name"]}': {grade["grade"]}")
        if grade["grade"] == "fail":
            self.state["queries_list"] = grade["follow_up_keywords"]
            self.state["feedback"] = grade["feedback"]
            logging.info(f"> Feekback: {grade["feedback"]}")
        self.state["grade"] = grade["grade"]
