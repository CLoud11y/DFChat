from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class Query(BaseModel):
    role: str
    content: str

class InputData(BaseModel):
    dialogId: Optional[str]
    query: List[Query]