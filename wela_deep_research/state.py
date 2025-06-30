
from typing import Dict
from typing import List
from typing import Optional
from typing import TypedDict

class ReportState(TypedDict):
    topic: Optional[str]
    sections: Optional[List[Dict]]
    current_section_index: Optional[int]
