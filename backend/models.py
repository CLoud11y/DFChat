from typing import List, Optional
from pydantic import BaseModel


class Query(BaseModel):
    role: str
    content: str
    def serialize(self):
        return {"role": self.role, "content": self.content}

class InputData(BaseModel):
    dialogId: Optional[str]
    query: List[Query]

class RecordName(BaseModel):
    dialogId: str
    record_name: str