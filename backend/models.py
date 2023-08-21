from typing import List, Optional
from pydantic import BaseModel
from fastapi import UploadFile

class Query(BaseModel):
    role: str
    content: str

class InputData(BaseModel):
    dialogId: Optional[str]
    query: List[Query]

class InputFiles(BaseModel):
    files: Optional[List[UploadFile]]
    input_data: InputData