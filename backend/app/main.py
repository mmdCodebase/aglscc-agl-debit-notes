from fastapi import FastAPI, Request, HTTPException, Depends
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.router import health, data, file, email, action
import agl_python_helpers.agl_email_helpers.email_attachment_helpers as em
from fastapi_utils.tasks import repeat_every


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
        expose_headers=["Content-Disposition"],
    ),
]

app = FastAPI(title=settings.PROJECT_NAME, middleware=middleware)

app.include_router(data.router, prefix="/V1")
app.include_router(file.router, prefix="/V1")
app.include_router(email.router, prefix="/V1")
app.include_router(action.router, prefix="/V1")
app.include_router(health.router)

def create_debit_note_inbox():
    return em.EmailAttachmentHelpers(email_account='agl-email-test', shared_resource='debitnote@aglsupplychain.com')

def get_debit_note_inbox():
    return app.state.debit_note_inbox

@app.on_event("startup")
@repeat_every(seconds=60 * 10)  # 1 hour
async def startup_event():
    try:
        del app.state.debit_note_inbox
        print('remove old api token')
    except Exception as e:
        print(e)

    app.state.debit_note_inbox = create_debit_note_inbox()
    print('Refresh API token')

@app.on_event("startup")        
@repeat_every(seconds=60 * 60)  # 1 hour
def cleanup_old_mails():
    from app.service.ms_graph import get_debit_note_emails
    from app.db.crud import email_crud
    from app.main import create_debit_note_inbox
    import requests

    data = email_crud.get_all_email_status(email_status_id=4)
    inbox = create_debit_note_inbox()

    for email in data:
        response = requests.get(
                    inbox.GRAPH_API_ENDPOINT + '/messages/{0}'.format(email.email_id),
                    headers=inbox.headers
                )
        if response.status_code == 404:
            print("not found")
            email_crud.update_entry(email_id=email.email_id, email_status_id=6)