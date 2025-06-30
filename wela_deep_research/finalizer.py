
from wela_agents.agents.workflow import StatefulAgent

class Finalizer(StatefulAgent):

    def __init__(self, *, state, input_key, output_key):
        super().__init__(state=state, input_key=input_key, output_key=output_key)

    def predict(self, **kwargs):
        report = "\n\n".join(section["Content"] for section in self.state["sections"])
        return report
