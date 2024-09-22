from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import List, Optional, Dict, Union
from itertools import groupby
from enum import Enum


class ChargeCode(str, Enum):
    FRT = "FRT"
    AGEN = "AGEN"
    AMS = "AMS"
    EQUIP = "EQUIP"
    ORIGIN = "ORIGIN"
    LOCAL = "LOCAL"
    PP = "PP"
    TERFEE = "TERFEE"
    TELEX = "TELEX"
    VGM = "VGM"
    DCART = "DCART"
    SEAL = "SEAL"
    DOC = "DOC"
    BOOK = "BOOK"
    CCLR = "CCLR"
    ALINE = "ALINE"
    PSEC = "PSEC"
    EGF = "EGF"
    TRANS = "TRANS"
    CHRENT = "CHRENT"


class OrgCode(str, Enum):
    # SEAVN  = "SEAVN"
    # SEATIA = "SEATIA"
    # SEAXAM = "SEAXAM"
    SEATWN = "SEATWN"
    SEAHKG = "SEAHKG"
    SEASHA = "SEASHA"
    SEAMAL = "SEAMAL"
    NINGBOJIRI = "NINGBOJIRI"
    # SEADAL = "SEADAL"
    # SEATAO = "SEATAO"
    # SEASZX = "SEASZX"
    # SEANGB = "SEANGB"
    # SEAFUZ = "SEAFUZ"


class DebitNoteCharges(BaseModel):
    id: Optional[int] = None
    charge_code: ChargeCode = ChargeCode.ORIGIN
    description: Optional[str] = None
    charges_in_usd: Optional[Union[float, str]] = None

    @field_validator("charges_in_usd")
    def validate_charges_in_usd(cls, v):
        if v == "":
            return 0
        return v


class DebitNoteAmount(BaseModel):
    currency: Optional[str] = None
    amount: Optional[float] = None


class DebitNoteData(BaseModel):
    email_id: Optional[str] = None
    debit_note_id: Optional[int] = None
    agl_shipment_number: Optional[str] = None
    creditor: Optional[str] = None
    invoice_num: Optional[str] = None
    invoice_date: Optional[date] = date.today()
    supplier_cost_ref: Optional[str] = None
    ar_ap: Optional[str] = "AP"
    is_post: Optional[str] = None
    charges: Optional[List[DebitNoteCharges]] = None
    subject: Optional[str] = None
    


class DebitNote(BaseModel):
    debit_note_number: Optional[str] = None
    email_id: Optional[str] = None
    agl_shipment_number: Optional[str] = None
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    invoice_date: Optional[date] = None
    customer_id: Optional[str] = None
    shipment: Optional[str] = None
    due_date: Optional[date] = None
    terms: Optional[str] = None
    consol_number: Optional[str] = None
    printed_by: Optional[str] = None
    shipper: Optional[str] = None
    consignee: Optional[str] = None
    order_numbers: Optional[List[str]] = None
    goods_description: Optional[str] = None
    import_customs_broker: Optional[str] = None
    weight: Optional[str] = None
    volume: Optional[str] = None
    chargeable_packages: Optional[str] = None
    vessel_voyage_imo: Optional[str] = None
    ocean_bill_of_lading: Optional[str] = None
    house_bill_of_lading: Optional[str] = None
    origin: Optional[str] = None
    etd: Optional[date] = None
    destination: Optional[str] = None
    eta: Optional[date] = None
    container_number: Optional[List[str]] = None
    container_size: Optional[List[str]] = None
    charges: Optional[List[DebitNoteCharges]] = None
    invoiced_amount: Optional[DebitNoteAmount] = None
    balance_due: Optional[DebitNoteAmount] = None
    payment_method: Optional[str] = None
    payment_due_date: Optional[date] = None
    creditor: Optional[OrgCode] = None

    def group_charges_by_code(self):
        if not self.charges:
            return

        combined_charges: Dict[ChargeCode, DebitNoteCharges] = {}

        for charge in self.charges:
            if charge.charge_code in combined_charges:
                existing_charge = combined_charges[charge.charge_code]
                existing_charge.charges_in_usd += charge.charges_in_usd or 0
                if charge.description:
                    if existing_charge.description:
                        existing_charge.description += f", {charge.description}"
                    else:
                        existing_charge.description = charge.description
            else:
                combined_charges[charge.charge_code] = DebitNoteCharges(
                    charge_code=charge.charge_code,
                    description=charge.description,
                    charges_in_usd=charge.charges_in_usd,
                )
        self.charges = list(combined_charges.values())

    def set_grouped_charges(
        self, grouped_charges: Dict[ChargeCode, List[DebitNoteCharges]]
    ):
        self.charges = [
            charge for charges in grouped_charges.values() for charge in charges
        ]


class DebitNoteCWUpload(BaseModel):
    email_id: Optional[str] = None
    agl_shipment_number: Optional[str] = None
    creditor: Optional[str] = None
    invoice_num: Optional[str] = None
    invoice_date: Optional[date] = None
    supplier_cost_ref: Optional[str] = None
    ar_ap: Optional[str] = None
    is_post: Optional[str] = None
    updated_at: Optional[datetime] = None
    FRT: Optional[float] = None
    AGEN: Optional[float] = None
    AMS: Optional[float] = None
    EQUIP: Optional[float] = None
    ORIGIN: Optional[float] = None
    LOCAL: Optional[float] = None
    PP: Optional[float] = None
    TERFEE: Optional[float] = None
    TELEX: Optional[float] = None
    VGM: Optional[float] = None
    DCART: Optional[float] = None
    SEAL: Optional[float] = None
    DOC: Optional[float] = None
    BOOK: Optional[float] = None
    CCLR: Optional[float] = None
    ALINE: Optional[float] = None
    PSEC: Optional[float] = None
    EGF: Optional[float] = None
    TRANS: Optional[float] = None
    CHRENT: Optional[float] = None
