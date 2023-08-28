import json
import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from utils.security import get_current_user
from database import DialogRecord
from models import RecordName

dialog_record_router = APIRouter()
logger = logging.getLogger(__name__)

@dialog_record_router.get("/by_id/{dialog_id}")
# create a api to retrive dialog record by id
async def get_dialog_record_by_id(dialog_id: int,user: Dict[str, Any] = Depends(get_current_user)):
    dialog_record = DialogRecord.get_record_by_id(dialog_id)
    if not dialog_record:
        raise HTTPException(status_code=404, detail="对话记录不存在")
    if dialog_record.user.username != user['sub']:
        raise HTTPException(status_code=403, detail="你没有权限查看该对话")
    return {
            "dialog_id": dialog_record.id,
            "record_name": dialog_record.record_name,
            "dialog_content": json.loads(dialog_record.dialog_content),
            "file_path": dialog_record.file_path
        }


@dialog_record_router.get("/list")
# create a api to retrive dialog record by user
async def get_dialog_record_by_user(user: Dict[str, Any] = Depends(get_current_user)):
    dialog_records = DialogRecord.get_record_by_username(user['sub'])
    record_list = []
    for dialog_record in dialog_records:
        record_list.append({
            "dialog_id": dialog_record.id,
            "record_name": dialog_record.record_name,
            "dialog_content": None,
            "file_path": dialog_record.file_path
            })
    return record_list


@dialog_record_router.post("/update_record_name")
# create a api to update record_name by id
async def update_record_name_by_id(input: RecordName, user: Dict[str, Any] = Depends(get_current_user)):
    dialog_record = DialogRecord.get_record_by_id(input.dialogId)
    if dialog_record.user.username != user['sub']:
        raise HTTPException(status_code=403, detail="你没有权限查看该对话")
    
    DialogRecord.update_record_name(input.dialogId, input.record_name)
    return "success"


@dialog_record_router.delete("/id/{dialog_id}")
# create a api to delete dialog record by id
async def delete_dialog_record_by_id(dialog_id: int, user: Dict[str, Any] = Depends(get_current_user)):
    dialog_record = DialogRecord.get_record_by_id(dialog_id)
    if not dialog_record:
        raise HTTPException(status_code=404, detail="对话记录不存在")
    if dialog_record.user.username != user['sub']:
        raise HTTPException(status_code=403, detail="你没有权限删除该对话")
    DialogRecord.delete_by_id(dialog_id)
    return "删除成功"