import json
import logging
import time
from typing import Any, Dict, Generator
from fastapi import APIRouter, Depends
import openai
from models import InputData, Query
from typing import List
from sse_starlette.sse import EventSourceResponse
from config import completion_engine_gpt35
from utils.security import get_current_user
from database import DialogRecord,User
from my_langchain import MyAgent, QAChain


gpt4_api = APIRouter()
logger = logging.getLogger(__name__)


def gpt4_streamer(input_data: InputData,user_name:str) -> Generator[str, Any, None]:
    request_messages = input_data.query

    try:
        whole_response : str = ""
        for chunk in openai.ChatCompletion.create(
                    engine=completion_engine_gpt35,
                    messages=[i.serialize() for i in request_messages],
                    stream=True,
                ):
                    content = chunk["choices"][0].get("delta", {}).get("content") # type: ignore
                    if content is not None:
                        whole_response += content
                        yield f"{content}"
        logger.info("The whole response is %s", whole_response)
        request_messages.append(Query(role="assistant", content=whole_response))
        yield update_dialog(input_data.dialogId, user_name, request_messages)
    except Exception as e:
        logger.exception(f"出错: {e}")
        yield "服务器太忙，请重试"


def langchain_streamer(input_data: InputData,user_name:str) -> Generator[str, Any, None]:
    chat_history = input_data.query[:-1]
    request_messages = input_data.query
    message = request_messages[-1].content
    try:
        # just for testing
        if request_messages[-2].content == "All files have been uploaded successfully! Ask questions about them":
            myAgent = QAChain(chat_history=chat_history, dialog_id = input_data.dialogId)
        else:
            myAgent = MyAgent(chat_history=chat_history, handle_parsing_errors=True)
        whole_response = myAgent.run(message)
        for chunk in whole_response:
            time.sleep(0.01)
            yield chunk
        logger.info("The whole response is %s", whole_response)
        request_messages.append(Query(role="assistant", content=whole_response))
        yield update_dialog(input_data.dialogId, user_name, request_messages)
    except Exception as e:
        logger.exception(f"出错: {e}")
        yield "服务器太忙，请重试"


def vue_test(input_data: InputData, user_name:str) -> Generator[str, Any, None]:
    '''for vue test. this method return the user input without using LLM'''
    time.sleep(3)
    request_messages = input_data.query
    try:
        whole_response:str = ""
        for token in request_messages[-1].content:
            whole_response += token
            yield f"{token}"
        logger.info("The whole response is %s", whole_response)
        request_messages.append(Query(role="assistant", content=whole_response))
        yield update_dialog(input_data.dialogId, user_name, request_messages)
    except Exception as e:
        logger.exception(f"出错: {e}")
        yield "服务器太忙，请重试"


def update_dialog(dialog_id: str, user_name: str, whole_messages: List[Query]) -> str:
    '''
    if create a new dialog, return f"dialogIdComplexSubfix82jjivmpq90doqjwdoiwq:{str(dialog_record.id)}"
    else return ""
    '''
    whole_json_messages = [i.serialize() for i in whole_messages]
    if dialog_id:
        DialogRecord.update_record(int(dialog_id),json.dumps(whole_json_messages, ensure_ascii=False))
        return ""
    else:
        user = User.get_user_by_user_name(user_name)
        dialog_record = DialogRecord.create_record(user.id,json.dumps(whole_json_messages, ensure_ascii=False))
        return f"dialogIdComplexSubfix82jjivmpq90doqjwdoiwq:{str(dialog_record.id)}"


@ gpt4_api.post("/sse")
async def process_data_sse(input_data: InputData, user: Dict[str, Any] = Depends(get_current_user)):
    # use Server-Sent Events to send data to client
    logger.debug("input_data: %s", input_data)
    # response_generator = langchain_streamer(input_data,user['sub'])
    # for vue test
    response_generator = vue_test(input_data,user['sub'])
    return EventSourceResponse(response_generator)
