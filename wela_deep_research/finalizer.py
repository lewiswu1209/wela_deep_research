
from typing import Any
from typing import Dict
from typing import Union
from typing import Generator
from wela_agents.agents.workflow import StatefulAgent

class Finalizer(StatefulAgent):

    def __init__(self, *, state: Dict[Any, Any], input_key: str, output_key: str) -> None:
        super().__init__(state=state, input_key=input_key, output_key=output_key)

    def predict(self, **kwargs: Any) -> Union[Any, Generator[Any, None, None]]:
        report = "\n\n".join(section["Content"] for section in self.state["sections"])
        return report
