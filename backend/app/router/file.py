from fastapi import APIRouter, Depends, HTTPException, Request, Query, Body, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Union, Optional
from app.service.s3 import s3_download_file
from io import BytesIO
from app.model.debit_notes import DebitNoteCWUpload
from datetime import datetime
from app.service.cw_upload import create_cw_upload_file
from app.db.crud import email_crud
from app.service.ms_graph import get_file_bytes
import agl_python_helpers.agl_email_helpers.email_attachment_helpers as em
import base64
import time

router = APIRouter(
    tags=["File"],
    responses={404: {"description": "Not found"}},
)

def get_debit_note_inbox():
    from app.main import app  # Local import to avoid circular dependency
    return app.state.debit_note_inbox


@router.get("/file")
async def get_file(
                file_name: Optional[str] = Query(None, description="Key of the file to download from S3"),
                email_id: Optional[str] = Query(None),
                debit_note_inbox = Depends(get_debit_note_inbox)
                ):
    try:
        if email_id:
            file_content=get_file_bytes(email_id, debit_note_inbox)
            file_content=base64.b64decode(file_content)

            
        else:
            file_content = s3_download_file(file_name, 'agl-debit-notes', file_name)

        response = StreamingResponse(BytesIO(file_content), media_type='application/octet-stream')
        response.headers['Content-Disposition'] = f'attachment; filename={file_name}'
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/file")
async def create_file(request: List[DebitNoteCWUpload]):
    file_name = f'CW1_NewChargeRate_UpSert_{datetime.now()}.xlsx'
    file_stream = create_cw_upload_file(request)
    response = StreamingResponse(file_stream, media_type='application/octet-stream')
    response.headers['Content-Disposition'] = f'attachment; filename={file_name}'
    for row in request:
        if row.email_id:
            email_crud.update_entry(email_id=row.email_id, email_status_id=7)
    return response