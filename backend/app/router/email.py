from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Union
from app.model.email import DebitNoteEmail
from app.db.crud import DebitNoteEmailCRUD

router = APIRouter(
    tags=["Emails"],
    responses={404: {"description": "Not found"}},
)

@router.get("/emails", response_model=List[DebitNoteEmail])
async def get_emails(email_status_id: int = Query(...)):
    try:    
        crud = DebitNoteEmailCRUD()
        return crud.read_entry_by_status_id(status_id=email_status_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to get emails {str(e)}')