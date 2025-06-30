
import logging

from wela_agents.schema.template.openai_chat import ChatTemplate
from wela_agents.schema.template.openai_chat import UserMessageTemplate
from wela_agents.schema.template.openai_chat import SystemMessageTemplate
from wela_agents.schema.template.prompt_template import StringPromptTemplate

from wela_deep_research.prompt import section_writer_inputs
from wela_deep_research.prompt import section_writer_instructions
from wela_deep_research.adapter import Adapter

class Writer(Adapter):

    def __init__(self, *, model, state, input_key, output_key):
        super().__init__(
            model=model,
            prompt_template=ChatTemplate(
                [
                    SystemMessageTemplate(
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

    def predict(self, **kwargs):
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
