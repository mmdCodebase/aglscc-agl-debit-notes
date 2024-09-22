from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Union
#from ..logging.logging import log_function_call, logger


router = APIRouter(
    tags=["Health"],
    responses={404: {"description": "Not found"}},
)

@router.get("/Health")
async def get_health():
    return True 