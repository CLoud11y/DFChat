from fastapi import APIRouter, Depends
from typing import Any, Dict
from utils.security import get_current_user
from models import Query
from database import DialogRecord, User
from config import base_dir
import logging
import os
import json
from typing import List
from fastapi import UploadFile

upload_api = APIRouter()
logger = logging.getLogger(__name__)


@upload_api.post("/upload_files/{dialogId}")
async def upload_files(files: List[UploadFile], dialogId: int, user: Dict[str, Any] = Depends(get_current_user)):
    '''
    save upload files to {base_dir}/upload_files/{user_name}/
    return dialogId
    '''
    user_name = user['sub']
    user = User.get_user_by_user_name(user_name)
    # make a dirctory for user according to user_name
    save_dir = base_dir + "upload_files/" + user_name + "/"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # save all files
    for each in files:
        save_path = save_dir + each.filename
        content = await each.read()
        await each.close()
        with open(save_path, "wb") as f:
            f.write(content)
    # append the messages saying that files have been uploaded
    record = DialogRecord.get_record_by_id(dialogId)
    messages: List[Query] = json.loads(record.dialog_content)
    messages.append(Query(role="assistant", content="All files have been uploaded successfully! Ask questions about them").serialize())
    if dialogId:
        DialogRecord.update_record(dialogId, json.dumps(messages, ensure_ascii=False), file_path=save_dir)
        return str(dialogId)
    else:
        dialog_record = DialogRecord.create_record(user.id, json.dumps(messages, ensure_ascii=False), file_path=save_dir)
        return str(dialog_record.id)


@upload_api.post("/upload_test/{dialogId}")
async def upload_test(files: List[UploadFile], dialogId: int, user: Dict[str, Any] = Depends(get_current_user)):
    logger.debug(files)
    logger.debug(type(files))
    logger.debug(dialogId)
    logger.debug(type(dialogId))
    record = DialogRecord.get_record_by_id(dialogId)
    messages = json.loads(record.dialog_content)
    logger.debug(messages)
    logger.debug(type(messages))
    return "success"
