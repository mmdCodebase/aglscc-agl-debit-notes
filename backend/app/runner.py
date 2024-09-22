#from app.service.data_extraction import extract_text_from_pdf, extract_json_data
from app.service.langchain import extract_json_data as extract_json_data_langchain, extract_text_from_pdf as extract_text_from_pdf_langchain
from app.service.ms_graph import get_debit_note_emails, download_debit_note_files
from app.service.s3 import s3_upload_file
from app.db.crud import DebitNoteEmailCRUD, DebitNoteCRUD
import re
from app.core.config import settings
'''
1. Get all debit_note emails
2. insert rows into debit_note_email table
3. Get each attachments
4. Extract debit note data
5. Insert debit note data
'''

emails = get_debit_note_emails()
email_crud = DebitNoteEmailCRUD()
debit_note_crud = DebitNoteCRUD

for email in emails:
    try:
        email_crud.create_entry(email_id=email['id'], subject=email['subject'], file_name = None, email_status_id=1)
    except Exception as e:
        print(e)

data = email_crud.get_all_email_status(email_status_id=1)

for debit_note_email in data:
    email = debit_note_email.to_dict()
    agl_shipment_number = email['subject']
    pattern = r'S\d+$'
    # Using re.search to find the pattern in the string
    match = re.search(pattern, agl_shipment_number)
    
    if match:
        agl_shipment_number = match.group()  # Get the matched string
        print("Extracted S number:", agl_shipment_number)
    else:
        print("No S number found in the input string.")

    files = download_debit_note_files(email)
    for file in files:
        #upload file into s3
        s3_upload_file(f"/tmp/{file}", 'agl-debit-notes', file)

        # extract pdf data as debit note model
        text = extract_text_from_pdf_langchain(f"/tmp/{file}")
        debit_note = extract_json_data_langchain(text)
        debit_note.agl_shipment_number = agl_shipment_number
        debit_note.email_id = email['id']
        
        #update email entry
        try:
            debit_note_id = debit_note_crud.insert_debit_note(debit_note=debit_note)
        except Exception as e:
            print(e)
        email_crud.update_entry(email_id=email['id'], file_name=file, email_status_id=4)
        
        try:
            debit_note_crud.insert_debit_note_charges(debit_note_id=debit_note_id, debit_note=debit_note)
        except Exception as e:
            print(e)
        
        

    # business logic for charge codes and creditor
    # move emails to other folder

