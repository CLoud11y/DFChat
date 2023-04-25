from typing import Any, Dict, List
from pydantic import BaseModel

class Query(BaseModel):
    type: str
    content: str

class InputData(BaseModel):
    query: List[Query]