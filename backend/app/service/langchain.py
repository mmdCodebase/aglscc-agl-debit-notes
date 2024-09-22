import os
from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.pydantic_v1 import BaseModel, Field, validator
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from app.model.debit_notes import DebitNote, DebitNoteCharges
from itertools import groupby
from typing import List


def extract_text_from_pdf(file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    return pages


def extract_json_data(pdf_data):
    load_dotenv()

    model_name = "gpt-3.5-turbo-0125"
    temperature = 0.0
    model = ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    parser = PydanticOutputParser(pydantic_object=DebitNote)
    prompt = PromptTemplate(
        template="""
        Extract data from this PDF file.\n Return dates as yyyy-mm-dd format
        Dates are usually displayed in dd-MMM-yy format
        Charge code H60 + L100 maps to charge_code "AGEN" for 60 and charge_code "LOCAL" for 100
        International Freight went under FRT charge_code
        Profit Share went under AGEN charge_code
        VGM Fee and VGM Weighing Fee went under VGM charge_code
        Documentation Fee went under DOC charge_code
        "Handling Fee - Origin" maps to charge_code AGEN
        charge_code FRT is for Freight Charges
        charge_code AGEN is for Agent Handling
        charge_code AMS is for AMS
        charge_code EQUIP is for Equipment Fee
        charge_code ORIGIN is for Origin Charges
        charge_code LOCAL is for Local Charge Difference
        charge_code PP is for Pier Pass
        charge_code TERFEE is for Terminal Fee
        charge_code TELEX is for TELEX FEE
        charge_code VGM is for Solas VGM Weight
        charge_code DCART is for Delivery Cartage
        charge_code SEAL is for Seal Fee
        charge_code DOC is for Documentation Fee
        charge_code BOOK is for Booking Management
        charge_code CCLR is for Customs Clearance
        charge_code ALINE is for Additional HTS Lines
        charge_code PSEC is for Port Security
        charge_code EGF is for Extended Gate Fee
        charge_code TRANS is for Whse Transloading
        charge_code CHRENT is for Chassis Rental
        SEAMASTER GLOBAL FORWARDING VIETNAM maps to creditor code: SEAVN
        SEAMASTER GLOBAL FORWARDING (SHANGHAI) LTD TIANJIN BRANCH maps to creditor code: SEASHA
        SEAMASTER GLOBAL FORWARDING (SHANGHAI) LTD XIAMEN BRANCH maps to creditor code: SEASHA
        SEAMASTER GLOBAL FORWARDING (TAIWAN) LTD maps to creditor code: SEATWN
        SEAMASTER GLOBAL FORWARDING (HONG KONG) LTD maps to creditor code: SEAHKG
        SEAMASTER GLOBAL FORWARDING (SHANGHAI) LTD DALIAN BRANCH maps to creditor code: SEASHA
        SEAMASTER GLOBAL FORWARDING (SHANGHAI) LTD maps to creditor code: SEASHA
        SEAMASTER GLOBAL FORWARDING (SHANGHAI) LTD QINGDAO BRANCH maps to creditor code: SEASHA
        SEAMASTER GLOBAL FORWARDING (SHANGHAI) LTD SHENZHEN BRANCH maps to creditor code: SEASHA
        SEAMASTER GLOBAL FORWARDING (MALAYSIA) LTD maps to creditor code: SEAMAL
        SEAMASTER GLOBAL FORWARDING (SHANGHAI) LTD NINGBO BRANCH maps to creditor code: SEASHA
        SEAMASTER GLOBAL FORWARDING (MALAYSIA) LTD maps to creditor code: SEAMAL
        SEAMASTER GLOBAL FORWARDING (SHANGHAI) LTD SHENZHEN BRANCH maps to creditor code: SEASHA
        SEAMASTER GLOBAL FORWARDING (SHANGHAI) LTD FUZHOU BRANCH maps to creditor code: SEASHA
        NINGBO JIRI SUPPLY CHAIN MANAGEMENT CO.,LTD maps to creditor code: NINGBOJIRI
        {format_instructions}
        {query}
        """,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    _input = prompt.format_prompt(query=pdf_data)
    output = model.invoke(_input.to_string())
    # The parsed_output variable now contains the structured data as a Pydantic model instance.
    try:
        parsed_output = parser.invoke(output)
        parsed_output.group_charges_by_code()
        return parsed_output
    except Exception as e:
        print(e)
        return DebitNote()
