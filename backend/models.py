from typing import List, Optional
from pydantic import BaseModel

class Query(BaseModel):
    role: str
    content: str

class InputData(BaseModel):
    dialogId: Optional[str]
    query: List[Query]