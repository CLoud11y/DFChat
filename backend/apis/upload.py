from fastapi import APIRouter, Depends
from typing import Any, Dict
from utils.security import get_current_user
from models import InputFiles, Query
from database import DialogRecord, User
from config import base_dir
import logging
import os
import json

upload_api = APIRouter()
logger = logging.getLogger(__name__)


@upload_api.post("/upload_files")
async def upload_files(input_files: InputFiles, user: Dict[str, Any] = Depends(get_current_user)):
    '''
    save upload files to {base_dir}/upload_files/{user_name}/
    return dialogId
    '''
    files = input_files.files
    input_data = input_files.input_data
    user_name = user['sub']
    user = User.get_user_by_user_name(user_name)
    # make a dirctory for user according to user_name
    save_dir = base_dir + "upload_files/" + user_name + "/"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir) 
    # save all files
    for each in files:
        save_path = save_dir + each.filename
        content = each.file.read()
        with open(save_path, "wb") as f:
            f.write(content)
    # append the messages saying that files have been uploaded
    request_messages = [d.serialize() for d in input_data.query]
    request_messages.append(Query(role="assistant", content="All files have been uploaded successfully! Ask questions about them").serialize())
    if input_data.dialogId:
        DialogRecord.update_record(int(input_data.dialogId), json.dumps(request_messages,ensure_ascii=False), file_path=save_dir)
        return input_data.dialogId
    else:
        dialog_record = DialogRecord.create_record(user.id, json.dumps(request_messages,ensure_ascii=False), file_path=save_dir)
        return str(dialog_record.id)
    
    