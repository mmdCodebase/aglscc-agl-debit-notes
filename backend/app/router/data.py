from fastapi import APIRouter, Depends, HTTPException, Request, Query, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Union
from app.model.debit_notes import DebitNoteData, DebitNoteCharges, DebitNoteCWUpload
from app.model.debit_note_email_status import DebitNoteEmailStatusEnum
from app.db.crud import DebitNoteCRUD, debit_note_crud
from app.model.debit_note_processor import DebitNoteProcessor

router = APIRouter(
    tags=["Data"],
    responses={404: {"description": "Not found"}},
)

@router.get("/data", response_model=DebitNoteData)
async def get_debit_note_data(file_name: str = Query(...)):
    try:
        debit_note = debit_note_crud.get_debit_note_by_file_name(file_name)
        charges = debit_note_crud.get_charges_by_debit_note_id(debit_note_id=debit_note.debit_note_id)
        charges = [DebitNoteCharges(id=charge[0], charge_code=charge[1], description=charge[2], charges_in_usd=charge[3]) for charge in charges]
        debit_note_data = DebitNoteData( 
            email_id=debit_note.email_id,
            debit_note_id=debit_note.debit_note_id,
            invoice_date=debit_note.invoice_date,
            agl_shipment_number=debit_note.agl_shipment_number,
            supplier_cost_ref=debit_note.supplier_cost_ref,
            creditor=debit_note.creditor,
            charges=charges,
            subject=debit_note.subject
        )
        return debit_note_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to load invoice data for file {file_name}, {str(e)}')

@router.get("/data/CWUpload", response_model=List[DebitNoteCWUpload]
            )
async def get_cw_upload_template_data(action_type: DebitNoteEmailStatusEnum = Query(...)):
    try:
        email_status_id = {
            DebitNoteEmailStatusEnum.CREATED: 1, 
            DebitNoteEmailStatusEnum.PENDING_DATA_EXTRACTION: 2, 
            DebitNoteEmailStatusEnum.FAILED: 3, 
            DebitNoteEmailStatusEnum.READY_FOR_REVIEW: 4, 
            DebitNoteEmailStatusEnum.PENDING_CW_UPLOAD: 5, 
            DebitNoteEmailStatusEnum.SKIPPED: 6,
            DebitNoteEmailStatusEnum.DOWNLOADED: 7,
        }.get(action_type, None)
        
        if email_status_id is None:
            return []

        debit_notes = []
        data = debit_note_crud.get_charges_by_email_status_id_cw(email_status_id=email_status_id)
        for row in data:
            row_dict = dict(row._mapping)
            debit_note = DebitNoteCWUpload(**row_dict)
            debit_notes.append(debit_note)
        
        return debit_notes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to get data for {action_type}, {str(e)}')
    
@router.post("/data")
async def generate_debit_note_data(background_tasks: BackgroundTasks):
    try:
        processor = DebitNoteProcessor()
        background_tasks.add_task(processor.process_debit_notes)
        return True
    except Exception as e:
        print(e)