
import logging
import argparse

from typing import Dict
from typing import Optional
from wela_agents.agents.workflow import END
from wela_agents.agents.workflow import START
from wela_agents.agents.workflow import Workflow
from wela_agents.models.openai_chat import OpenAIChat

from .state import ReportState
from .grader import Grader
from .writer import Writer
from .writer import Concluder
from .writer import Introducer
from .planner import Planner
from .finalizer import Finalizer
from .summarizer import Summarizer
from .websearcher import WebSearcher
from .queries_generator import QueriesGenerator

def section_condition(state: ReportState) -> bool:
    if state["grade"] == "fail":
        return "rewrite_this_section"
    elif state["current_section_index"] < len(state["sections"]) - 2:
        state["current_section_index"] += 1
        return "write_next_section"
    else:
        state["current_section_index"] += 1
        return "write_rest_section"

def deep_rearch(model: OpenAIChat, state: ReportState, topic:str, google_api_key: str, search_engine_id: str, proxies: Optional[Dict[str, str]] = None):
    planner = Planner(state=state, model=model, input_key="input", output_key="output")
    queries_generator = QueriesGenerator(state=state, model=model, input_key="input", output_key="output")
    searcher = WebSearcher(
        state=state,
        proxies=proxies,
        google_api_key=google_api_key,
        search_engine_id=search_engine_id,
        input_key="input",
        output_key="output"
    )
    summarizer = Summarizer(state=state, model=model, proxy=proxies["http"], input_key="input", output_key="output")
    writer = Writer(state=state, model=model, input_key="input", output_key="output")
    grader = Grader(state=state, model=model, input_key="input", output_key="output")
    concluder = Concluder(state=state, model=model, input_key="input", output_key="output")
    introducer = Introducer(state=state, model=model, input_key="input", output_key="output")
    finalizer = Finalizer(state=state, input_key="input", output_key="output")

    workflow = Workflow(state=state, input_key="input", output_key="output")
    workflow.add_mapping(START, planner)
    workflow.add_mapping(planner, queries_generator)
    workflow.add_mapping(queries_generator, searcher)
    workflow.add_mapping(searcher, summarizer)
    workflow.add_mapping(summarizer, writer)
    workflow.add_mapping(writer, grader)
    workflow.add_conditional_mapping(
        grader,
        section_condition,
        {
            "rewrite_this_section": searcher,
            "write_next_section": queries_generator,
            "write_rest_section": concluder
        }
    )
    workflow.add_mapping(concluder, introducer)
    workflow.add_mapping(introducer, finalizer)
    workflow.add_mapping(finalizer, END)

    result = workflow.predict(topic=topic)
    return result

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    parser = argparse.ArgumentParser(description="A clone of Wela, a researcher.")
    parser.add_argument("--topic", help="topic")
    parser.add_argument("--path", help="file path to save")
    parser.add_argument("--model", help="model name")
    parser.add_argument("--api_key", help="openai api key")
    parser.add_argument("--base_url", help="openai api endpoint")
    parser.add_argument("--proxy", help="proxy")
    parser.add_argument("--google_api_key", help="google_api_key")
    parser.add_argument("--search_engine_id", help="search_engine_id")
    args = parser.parse_args()

    if args.topic and args.path and args.api_key and args.google_api_key and args.search_engine_id:
        state = ReportState()
        model = OpenAIChat(
            model_name=args.model if args.model else "gpt-4",
            stream=False,
            api_key=args.api_key,
            base_url=args.base_url if args.base_url else "https://api.openai.com/v1/"
        )
        result = deep_rearch(
            model=model,
            state=state,
            topic=args.topic,
            proxies=
            {
                "http": args.proxy,
                "https": args.proxy
            } if args.proxy else None,
            google_api_key=args.google_api_key,
            search_engine_id=args.search_engine_id
        )
        with open(args.path, "w", encoding="utf-8") as file:
            file.write(result)
    else:
        print(parser.format_usage())
