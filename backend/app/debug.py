from app.db.crud import email_crud
from app.service.ms_graph import get_file_bytes
import agl_python_helpers.agl_email_helpers.email_attachment_helpers as em
import base64
from app.service.s3 import s3_download_file
import logging 

logger = logging.getLogger(__name__)
logging.basicConfig(filename='file_mismatch.log', level=logging.INFO)


data = email_crud.get_all_email_status(email_status_id=4)
debit_note_inbox = em.EmailAttachmentHelpers(email_account='agl-email-test', shared_resource='debitnote@aglsupplychain.com')

for email in data:
    try:
        graph_file_content=get_file_bytes(email.email_id, debit_note_inbox)
        graph_file_content=base64.b64decode(graph_file_content)
    
        s3_file_content = s3_download_file(email.file_name, 'agl-debit-notes', email.file_name)
        if graph_file_content != s3_file_content:
            print(email.file_name, email.email_id)
            logging.error(f"File Mismatch: {email.file_name}, {email.email_id}")
    except:
        pass