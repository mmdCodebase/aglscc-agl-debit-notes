from app.service.langchain import extract_json_data as extract_json_data_langchain, extract_text_from_pdf as extract_text_from_pdf_langchain
from app.service.ms_graph import get_debit_note_emails, download_debit_note_files
from app.service.s3 import s3_upload_file
from app.db.crud import DebitNoteEmailCRUD, DebitNoteCRUD
import re
from app.core.config import settings
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)
logging.basicConfig(filename='debit_note_processor.log', level=logging.INFO)

class DebitNoteProcessor:
    def __init__(self):
        self.email_crud = DebitNoteEmailCRUD()
        self.debit_note_crud = DebitNoteCRUD()

    def process_debit_notes(self):
        emails = get_debit_note_emails()

        for email in emails:
            try:
                self._process_email(email)
            except Exception as e:
                print(e)

    def _process_email(self, email):
        # Insert into debit_note_email
        self._create_email_entry(email)

        #Grab inserted emails
        data = self.email_crud.read_entry_by_email_id(email_id=email['id'])

        for debit_note_email in data:
            email_data = debit_note_email.to_dict()
            logging.info(f"Email Data: {email_data}")

            agl_shipment_number = self._extract_agl_shipment_number(email_data['subject'])
            logging.info(f"Downloading: {email['id']}")
            #using email_data object will potentially save the issue
            files = download_debit_note_files(email_data)
            logging.info(f"files downloaded: {files}")
            for file in files:
                try:
                    self._process_file(file, agl_shipment_number, email_data)
                except Exception as e:
                    print(e)

    def _create_email_entry(self, email):
        self.email_crud.create_entry(
            email_id=email['id'],
            subject=email['subject'],
            file_name=None,
            email_status_id=1
        )

    def _extract_agl_shipment_number(self, subject):
        pattern = r'S\d+$'
        match = re.search(pattern, subject)
        
        if match:
            return match.group()
        else:
            print("No S number found in the input string.")
            return None

    def _process_file(self, file, agl_shipment_number, email_data):
        email_id = email_data['id']
        logging.info(f"start: {file}, {agl_shipment_number} {email_id}")
        s3_upload_file(f"/tmp/{file}", 'agl-debit-notes', file)
        text = extract_text_from_pdf_langchain(f"/tmp/{file}")
        debit_note = extract_json_data_langchain(text)
        debit_note.agl_shipment_number = agl_shipment_number
        debit_note.email_id = email_data['id']

        try:
            email_id = email_data["id"]
            logging.info(f"Update to status=4: {file}, {agl_shipment_number} {email_id}")
            debit_note_id = self.debit_note_crud.insert_debit_note(debit_note=debit_note)
            self._update_email_entry(email_data['id'], file)
            self._insert_debit_note_charges(debit_note_id, debit_note)
            logging.info(f"success: {file}, {agl_shipment_number} {email_data}")
        except Exception as e:
            print(e)
            logging.error(f"failed: {file}, {agl_shipment_number} {email_data} {str(e)}")


    def _update_email_entry(self, email_id, file_name):
        logging.info(f"Update to status=4: {file_name}, {email_id}")
        self.email_crud.update_entry(email_id=email_id, file_name=file_name, email_status_id=4)

    def _insert_debit_note_charges(self, debit_note_id, debit_note):
        self.debit_note_crud.insert_debit_note_charges(debit_note_id=debit_note_id, debit_note=debit_note)

if __name__ == "__main__":
    processor = DebitNoteProcessor()
    processor.process_debit_notes()