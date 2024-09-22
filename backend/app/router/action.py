from fastapi import APIRouter, Depends, HTTPException, Request, Query, Body
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Union, Optional
from app.model.debit_note_email_status import DebitNoteEmailStatusEnum
from app.model.debit_notes import DebitNoteData
from app.db.crud import email_crud, debit_note_crud
from app.service.ms_graph import move_debit_note_emails
from app.core.config import settings
import logging
router = APIRouter(
    tags=["Action"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)
logging.basicConfig(filename='debit_note_action.log', level=logging.INFO)

@router.post("/actions")
async def run_action(
    debit_note_data: Optional[DebitNoteData] = Body(None),
    email_id: str = Query(...),
    action_type: DebitNoteEmailStatusEnum = Query(...),
):
    if action_type == DebitNoteEmailStatusEnum.SKIPPED:
        # Update email status
        # Move email to folder
        if move_debit_note_emails(email_id, f"{settings.FASTAPI_ENVIRONMENT}_skipped"):
            email_crud.update_entry(email_id=email_id, email_status_id=6)
            return JSONResponse(
                status_code=200,
                content={
                    "message": f"Email {email_id} has been skipped and moved to the skipped folder."
                },
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to move email {email_id} to the skipped folder.",
            )

    if action_type == DebitNoteEmailStatusEnum.PENDING_CW_UPLOAD:
        try:
            # Update the data to CW upload staging
            update_data_dict = debit_note_data.model_dump()
            update_data_dict.pop("debit_note_id")
            update_data_dict.pop("subject")
            update_data_dict["debit_note_number"] = update_data_dict.pop("supplier_cost_ref")
            update_data_dict.pop("charges")

            debit_note_crud.update_debit_note_by_id(
                debit_note_id=debit_note_data.debit_note_id,
                update_data=update_data_dict,
            )
            for charge in debit_note_data.charges:
                if charge.id:
                    logging.info(f"Updating charge: {charge}")
                    debit_note_crud.update_charges_by_charge_id(charge_id=charge.id, update_data=charge.dict())
                
                else:
                    logging.info(f"Inserting charge: {charge}")
                    logging.info(f"Debit note id: {debit_note_data.debit_note_id}")
                    debit_note_crud.insert_debit_note_charge(debit_note_id=debit_note_data.debit_note_id, debit_note_charge=charge)

            # Update Email Status
            email_crud.update_entry(email_id=email_id, email_status_id=5)

            # Move email to processed folder
            move_debit_note_emails(
                email_id, f"{settings.FASTAPI_ENVIRONMENT}_processed"
            )

            return JSONResponse(
                status_code=200,
                content={
                    "message": f"Email {email_id} has been successfully processed and moved to the processed folder."
                },
            )
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to perform {action_type} for {debit_note_data.agl_shipment_number}, {str(e)}",
            )

    return JSONResponse(
        status_code=200, content={"message": f"No action taken for email {email_id}."}
    )
