from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class DebitNoteEmail(BaseModel):
    email_id: Optional[str] = None
    file_name: Optional[str] = None
