import agl_python_helpers.agl_email_helpers.email_attachment_helpers as em
from app.core.config import settings
import shortuuid


def get_debit_note_emails():
    debit_note_inbox = em.EmailAttachmentHelpers(email_account='agl-email-test',shared_resource='debitnote@aglsupplychain.com')
    #debit_note_inbox.find_emails_all()
    if settings.FASTAPI_ENVIRONMENT == 'prod':
        folder_name ='inbox'
    else:
        folder_name ='test'

    folder_id = debit_note_inbox.get_folder_id_by_name(folder_name=folder_name)

    params = {
        '$top': 1000,
        '$filter': "ReceivedDateTime ge 2024-05-01" 
    }
    debit_note_inbox.find_email_by_folder_id(folder_id=folder_id, params=params)
    return debit_note_inbox.emails

def download_debit_note_files(email):
    debit_note_inbox = em.EmailAttachmentHelpers(email_account='agl-email-test',shared_resource='debitnote@aglsupplychain.com')
    file_names = debit_note_inbox.download_email_attachments(email, save_folder='/tmp', file_prefix =shortuuid.uuid())
    return file_names

def move_debit_note_emails(email_id, folder_name):
    try:
        debit_note_inbox = em.EmailAttachmentHelpers(email_account='agl-email-test',shared_resource='debitnote@aglsupplychain.com')
        folder_id = debit_note_inbox.get_folder_id_by_name(folder_name)
        debit_note_inbox.move_email_to_folder_id(email_id, folder_id)
    except Exception as e:
        print(e)
        raise
    return True

def get_file_bytes(email_id, debit_note_inbox):
    #debit_note_inbox = em.EmailAttachmentHelpers(email_account='agl-email-test',shared_resource='debitnote@aglsupplychain.com')
    folder_id = debit_note_inbox.get_folder_id_by_name(folder_name='inbox')
    params = {
        '$top': 1000,
        '$filter': "ReceivedDateTime ge 2024-05-01" 
    }
    email = {"id": email_id}
    #debit_note_inbox.find_email_by_folder_id(folder_id=folder_id, params=params)
    attachments = debit_note_inbox.fetch_email_attachments(email)
    try:
        bytes = attachments[0]['contentBytes']
    except Exception as e:
        print(e)
        bytes = ''
        raise e
    return bytes