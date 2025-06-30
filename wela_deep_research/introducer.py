
import logging

from wela_agents.models.openai_chat import OpenAIChat
from wela_agents.schema.template.openai_chat import ChatTemplate
from wela_agents.schema.template.openai_chat import UserMessageTemplate
from wela_agents.schema.template.openai_chat import SystemMessageTemplate
from wela_agents.schema.template.prompt_template import StringPromptTemplate

from wela_deep_research.state import ReportState
from wela_deep_research.prompt import Introduction_section_writer_instructions
from wela_deep_research.adapter import Adapter

class Introducer(Adapter):

    def __init__(self, *, model: OpenAIChat, state: ReportState, input_key: str, output_key: str):
        super().__init__(
            model=model,
            prompt_template=ChatTemplate(
                [
                    SystemMessageTemplate(
                        StringPromptTemplate(Introduction_section_writer_instructions)
                    ),
                    UserMessageTemplate(
                        StringPromptTemplate(
                            "Generate a report section based on the provided sources. Use same language as the report topic, e.g. if the report topic is in Chinese, use Chinese for section names and descriptions"
                        )
                    )
                ]
            ),
            state=state,
            input_key=input_key,
            output_key=output_key
        )

    def __format_sections(self):
        formatted_str = ""
        for idx, section in enumerate(self.state["sections"], 1):
            formatted_str += f"""
{'='*60}
Section {idx}: {section["Name"]}
{'='*60}
Description:
{section["Description"]}
Requires Research: 
{section["Research"]}
Content:
{section.get("Content") if section.get("Content", None) else "[Not yet written]"}

"""
        return formatted_str

    def predict(self, **kwargs):
        section = self.state["sections"][0]
        logging.info(f"> Finalizing section: '{section["Name"]}'")
        kwargs["section_name"] = section["Name"]
        kwargs["section_description"] = section["Description"]
        kwargs["context"] = self.__format_sections()
        response = super().predict(**kwargs)["content"]
        section["Content"] = response
        logging.info(f"Finalized section '{section["Name"]}': {section["Content"][:100]}...")
