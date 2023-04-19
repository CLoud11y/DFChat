from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import openai
from typing import Any, Dict, List
import logging
from enums import API_MODE
from config import api_type, api_url, api_key, api_version, completion_engine_gpt4

if api_type == API_MODE.OPEN_AI:
    raise Exception("OpenAI API is not supported yet")
elif api_type == API_MODE.AZURE:
    openai.api_type = api_type.name
    openai.api_base = api_url
    openai.api_key = api_key
    openai.api_version = api_version


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
app = FastAPI(check_content_type=False)
api_router = APIRouter()

class InputData(BaseModel):
    query: List[Any]

@api_router.post("/api/gpt4")
async def process_data(input_data: InputData):
    try:
        logger.debug("input_data: %s", input_data)
        requst_messages = []
        for d in input_data.query:
            role = 'assistant' if d['type'] == 'system' else 'user'
            requst_messages.append({"role": role, "content": d['content']})

        response = openai.ChatCompletion.create(
        engine=completion_engine_gpt4,
        # temperature=0.5,
        messages= requst_messages
        # [
            # {'role':'system',"content":"You are a helpful assistant whose job is to answer user questions based on the provided context. When answering questions, you should strive to preserve as much relevant information from the context as possible."},
            # {"role": "user", "content": input_data.query}]
        )
        logger.debug("response: %s", response)
        logger.info(f"Get response with Id:{response['id']},model:{response['model']},usage(comp,prompt,total):{list(response['usage'].values())}")
        return response['choices'][0]['message']['content']
    except Exception as e:
        logger.exception("openai服务请求出错")
        return "服务器太忙，请重试"

app.include_router(api_router)
@app.get("/")
def redirect_to_index():
    return RedirectResponse("/index.html")
app.mount("/", StaticFiles(directory="static"), name="static")