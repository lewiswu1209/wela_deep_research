
import logging

from typing import Any
from typing import Dict
from typing import Union
from typing import Generator
from wela_agents.models.openai_chat import OpenAIChat
from wela_agents.schema.template.openai_chat import ChatTemplate
from wela_agents.schema.template.openai_chat import UserMessageTemplate
from wela_agents.schema.template.prompt_template import StringPromptTemplate

from .state import ReportState
from .prompt import section_writer_inputs
from .prompt import section_writer_instructions
from .prompt import conclusion_section_writer_instructions
from .prompt import Introduction_section_writer_instructions
from .adapter import Adapter

def format_sections(sections: Dict):
    formatted_str = ""
    for idx, section in enumerate(sections, 1):
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

class Writer(Adapter):

    def __init__(self, *, model: OpenAIChat, state: ReportState, input_key: str, output_key: str) -> None:
        super().__init__(
            model=model,
            prompt_template=ChatTemplate(
                [
                    UserMessageTemplate(
                        StringPromptTemplate(section_writer_instructions)
                    ),
                    UserMessageTemplate(
                        StringPromptTemplate(section_writer_inputs)
                    )
                ]
            ),
            state=state,
            input_key=input_key,
            output_key=output_key
        )

    def predict(self, **kwargs: Any) -> Union[Any, Generator[Any, None, None]]:
        section = self.state["sections"][self.state["current_section_index"]]
        source_material = ""
        for search_item in self.state["search_results"]:
            if "summary" in search_item:
                source_material += f"""
{"="*60}
Title: {search_item["title"]}
{"="*60}
href: {search_item["link"]}
{"="*60}
Summary: {search_item["summary"]}
{"="*60}
"""
                if "key_excerpts" in search_item:
                    source_material += f"""Key Excerpts:
        {"\n".join(search_item["key_excerpts"])}

        """

        logging.info(f"> Writing section: '{section["Name"]}'")

        kwargs["section_name"] = section["Name"]
        kwargs["section_description"] = section["Description"]
        kwargs["section_content"] = section.get("Content", "[Not written yet]")
        kwargs["context"] = source_material
        kwargs["feedback"] = self.state["feedback"] if "feedback" in self.state else ""
        response = super().predict(**kwargs)["content"]
        section["Content"] = response
        logging.info(
f"""Written section '{section["Name"]}':
{section["Content"][:100]}...
"""
        )

class Introducer(Adapter):

    def __init__(self, *, model: OpenAIChat, state: ReportState, input_key: str, output_key: str) -> None:
        super().__init__(
            model=model,
            prompt_template=ChatTemplate(
                [
                    UserMessageTemplate(
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

    def predict(self, **kwargs: Any) -> Union[Any, Generator[Any, None, None]]:
        sections = self.state["sections"]
        section = sections[0]
        logging.info(f"> Finalizing section: '{section["Name"]}'")
        kwargs["section_name"] = section["Name"]
        kwargs["section_description"] = section["Description"]
        kwargs["context"] = format_sections(sections=sections)
        response = super().predict(**kwargs)["content"]
        section["Content"] = response
        logging.info(f"Finalized section '{section["Name"]}': {section["Content"][:100]}...")

class Concluder(Adapter):

    def __init__(self, *, model: OpenAIChat, state: ReportState, input_key: str, output_key: str) -> None:
        super().__init__(
            model=model,
            prompt_template=ChatTemplate(
                [
                    UserMessageTemplate(
                        StringPromptTemplate(conclusion_section_writer_instructions)
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

    def predict(self, **kwargs: Any) -> Union[Any, Generator[Any, None, None]]:
        sections = self.state["sections"]
        section = sections[self.state["current_section_index"]]

        logging.info(f"> Finalizing section: '{section["Name"]}'")

        kwargs["section_name"] = section["Name"]
        kwargs["section_description"] = section["Description"]
        kwargs["context"] = format_sections(sections=sections)
        response = super().predict(**kwargs)["content"]
        section["Content"] = response
        logging.info(f"> Finalized section '{section["Name"]}': {section["Content"][:100]}...")
