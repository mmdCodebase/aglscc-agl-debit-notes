import os
import fitz
import json
from openai import OpenAI
from dotenv import load_dotenv
from app.model.debit_notes import DebitNote, DebitNoteAmount, DebitNoteCharges


def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    text = ""

    # Iterate through the pages and extract text
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()

    return text

def create_prompt():

    text = extract_text_from_pdf('/Users/ilyoon-kim/Documents/agl-debit-notes/backend/app/assets/6wnnogf93qpWVj8wXs9rao-AMERICAN-DEBIT_NOTE_-_SSSHA6710121_A_-_AMEGLOATL_28-Jun-24_-_SSSHA67101212.PDF')

    with open("/Users/ilyoon-kim/Documents/agl-debit-notes/backend/app/assets/6wnnogf93qpWVj8wXs9rao-AMERICAN-DEBIT_NOTE_-_SSSHA6710121_A_-_AMEGLOATL_28-Jun-24_-_SSSHA67101212.json") as f:
        output_json = f.read()

    prompt = {
        "role": "system", 
        "content": f"{text} should output {output_json} in json format"
    }

    return prompt


load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def extract_json_data(data):

    messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON from PDF files."},
            {"role": "system", "content": f"overall json model looks like this {DebitNote.model_fields}"},
            {"role": "system", "content": f"DebitNoteCharges model looks like this {DebitNoteCharges().json()} used in CHARGES field"},
            {"role": "system", "content": f"DebitNoteAmount model looks like this {DebitNoteCharges().json()} used in INVOICE_AMOUNT and BALANCE_DUE field"},
            {"role": "system", "content": "Return dates in yyyy-mm-dd format"},
            {"role": "system", "content": "Container numbers are formatted as four-letter prefix, a six-digit serial number and one check digit"},
            {"role": "system", "content": "Container numbers are comma delimited strings"},
            {"role": "system", "content": "Container sizes are comma delimited strings"},
            {"role": "system", "content": "Possible container sizes include 20GP, 20, 40, 40GP, 40HC"},
            {"role": "system", "content": "Charges should be collected in total and not per container /container basis"},
            {"role": "user", "content": f"extract data in json format for me {data}"}
        ]
    messages.append(create_prompt())
    try:
        response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        response_format={ "type": "json_object" },
        temperature=0.2,
        messages=messages
        
    )
    except Exception as e:
        print(e)
    response_json = json.loads(response.choices[0].message.content)
    print(response_json)
    debit_note = DebitNote(**response_json)
    return debit_note
