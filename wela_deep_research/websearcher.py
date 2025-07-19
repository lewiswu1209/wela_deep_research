
import logging
import requests

from typing import Any
from typing import Dict
from typing import Union
from typing import Generator
from wela_agents.agents.workflow import StatefulAgent

from .state import ReportState

class WebSearcher(StatefulAgent):

    def __init__(self, *, state: ReportState, proxies: Dict[str, str], google_api_key: str, search_engine_id: str, num_of_result=3, input_key: str, output_key: str):
        self.__proxies = proxies
        self.__google_api_key = google_api_key
        self.__search_engine_id = search_engine_id
        self.__num_of_result = num_of_result
        super().__init__(state=state, input_key=input_key, output_key=output_key)

    def predict(self, **kwargs: Any) -> Union[Any, Generator[Any, None, None]]:
        queries_list = self.state["queries_list"]
        search_results = {}
        for query in queries_list:
            try:
                logging.info(f"> Performing web search for query: '{query}'")
                response = requests.get(
                    f"https://www.googleapis.com/customsearch/v1?q={query}+-filetype:pdf+-filetype:doc+-filetype:docx&key={self.__google_api_key}&cx={self.__search_engine_id}&num={self.__num_of_result}",
                    proxies=self.__proxies
                )
                for result in response.json().get("items", []):
                    search_results[result["link"]] = {
                        "title": result["title"],
                        "snippet": result["snippet"],
                        "link": result["link"]
                    }
            except Exception as e:
                logging.error(f"> Error when performing web search for query '{query}': {e}")
        self.state["search_results"] = list(search_results.values())

        for search_item in self.state["search_results"]:
            logging.info(f"> Search result: {search_item["title"]} - {search_item["link"]}")
