
import logging
from typing import Any, Dict, Generator, List
from fastapi import APIRouter
import openai
from models import InputData
from sse_starlette.sse import EventSourceResponse
from config import completion_engine_gpt4, completion_engine_gpt35


gpt4_api = APIRouter()
logger = logging.getLogger(__name__)

@gpt4_api.post("/standard")
async def process_data(input_data: InputData):
    try:
        logger.debug("input_data: %s", input_data)
        requst_messages = []
        for d in input_data.query:
            role = 'assistant' if d.type == 'system' else 'user'
            requst_messages.append({"role": role, "content": d.content})

        response = openai.ChatCompletion.create(
        engine=completion_engine_gpt4,
        # temperature=0.5,
        messages= requst_messages

        )
        logger.debug("response: %s", response)
        logger.info(f"Get response with Id:{response['id']},model:{response['model']},usage(comp,prompt,total):{list(response['usage'].values())}") # type: ignore
        return response['choices'][0]['message']['content'] # type: ignore
    except Exception as e:
        logger.exception("openai服务请求出错")
        return "服务器太忙，请重试"


def gpt4_streamer(request_messages: List[Dict[str,str]]) -> Generator[str, Any, None]:
    try:
        whole_response : str = ""
        for chunk in openai.ChatCompletion.create(
                    engine=completion_engine_gpt35,
                    messages=request_messages,
                    stream=True,
                ):
                    content = chunk["choices"][0].get("delta", {}).get("content") # type: ignore
                    if content is not None:
                        whole_response += content
                        yield f"{content}"
        logger.info("The whole response is %s", whole_response)
    except Exception as e:
        logger.exception("openai服务请求出错")
        yield "服务器太忙，请重试"

@ gpt4_api.post("/sse")
async def process_data_sse(input_data: InputData):
    # use Server-Sent Events to send data to client
    logger.debug("input_data: %s", input_data)
    request_messages = []
    for d in input_data.query:
        role = 'assistant' if d.type == 'system' else 'user'
        request_messages.append({"role": role, "content": d.content})

    return EventSourceResponse(gpt4_streamer(request_messages))

