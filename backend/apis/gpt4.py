
import json
import logging
from typing import Any, Dict, Generator, List
from fastapi import APIRouter, Depends
import openai
from models import InputData
from sse_starlette.sse import EventSourceResponse
from config import completion_engine_gpt4, completion_engine_gpt35
from utils.security import get_current_user
from database import DialogRecord,User


gpt4_api = APIRouter()
logger = logging.getLogger(__name__)

@gpt4_api.post("/standard")
async def process_data(input_data: InputData, user: Dict[str, Any] = Depends(get_current_user)):
    try:
        logger.debug("input_data: %s", input_data)
        requst_messages = []
        for d in input_data.query:
            role = 'assistant' if d.role == 'system' else 'user'
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


def gpt4_streamer(input_data: InputData,user_name:str) -> Generator[str, Any, None]:
    request_messages = []
    for d in input_data.query:
        request_messages.append({"role": d.role, "content": d.content})

    try:
        whole_response : str = ""
        for chunk in openai.ChatCompletion.create(
                    engine=completion_engine_gpt4,
                    messages=request_messages,
                    stream=True,
                ):
                    content = chunk["choices"][0].get("delta", {}).get("content") # type: ignore
                    if content is not None:
                        whole_response += content
                        yield f"{content}"
        logger.info("The whole response is %s", whole_response)
        request_messages.append({"role": "assistant", "content": whole_response})
        if input_data.dialogId:
            DialogRecord.update_record(int(input_data.dialogId),json.dumps(request_messages,ensure_ascii=False))
        else:
            user = User.get_user_by_user_name(user_name)
            dialog_record = DialogRecord.create_record(user.id,json.dumps(request_messages,ensure_ascii=False))
            yield f"dialogIdComplexSubfix82jjivmpq90doqjwdoiwq:{str(dialog_record.id)}"
    except Exception as e:
        logger.exception("openai服务请求出错")
        yield "服务器太忙，请重试"

@ gpt4_api.post("/sse")
async def process_data_sse(input_data: InputData, user: Dict[str, Any] = Depends(get_current_user)):
    # use Server-Sent Events to send data to client
    logger.debug("input_data: %s", input_data)
    return EventSourceResponse(gpt4_streamer(input_data,user['sub']))


