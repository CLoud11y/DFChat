from typing import List, Optional
from pydantic import BaseModel
from fastapi import UploadFile

class Query(BaseModel):
    role: str
    content: str
    def serialize(self):
        return {"role": self.role, "content": self.content}

class InputData(BaseModel):
    dialogId: Optional[str]
    query: List[Query]

class InputFiles(BaseModel):
    files: Optional[List[UploadFile]]
    input_data: InputData