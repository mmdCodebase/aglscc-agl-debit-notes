from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, Boolean, Date, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime
from .database import DebitNoteDB
from ..model.debit_note_email_status import DebitNoteEmailStatusEnum
from app.core.config import settings

db = DebitNoteDB()
engine = db.get_engine()

Base = declarative_base()

# Define the ORM class/table
class DebitNoteCharges(Base):
    __tablename__ = 'debit_note_charges'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=True)
    charge_code = Column(String, nullable=True)
    charges_in_usd = Column(Float, nullable=True)
    debit_note_id = Column(Integer, ForeignKey('debit_note.id'), nullable=False)

class DebitNoteAmount(Base):
    __tablename__ = 'debit_note_amount'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    currency = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    debit_note_id = Column(Integer, ForeignKey('debit_note.id'), nullable=False)

class DebitNote(Base):
    __tablename__ = 'debit_note'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(String, nullable=True)
    debit_note_number = Column(String, nullable=True)
    agl_shipment_number = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    company_address = Column(Text, nullable=True)
    invoice_date = Column(Date, nullable=True)
    customer_id = Column(String, nullable=True)
    shipment = Column(String, nullable=True)
    due_date = Column(Date, nullable=True)
    terms = Column(String, nullable=True)
    consol_number = Column(String, nullable=True)
    printed_by = Column(String, nullable=True)
    shipper = Column(String, nullable=True)
    consignee = Column(String, nullable=True)
    order_numbers= Column(String, nullable=True)
    goods_description = Column(Text, nullable=True)
    import_customs_broker = Column(String, nullable=True)
    weight = Column(String, nullable=True)
    volume = Column(String, nullable=True)
    chargeable_packages = Column(String, nullable=True)
    vessel_voyage_imo = Column(String, nullable=True)
    ocean_bill_of_lading = Column(String, nullable=True)
    house_bill_of_lading = Column(String, nullable=True)
    origin = Column(String, nullable=True)
    etd = Column(Date, nullable=True)
    destination = Column(String, nullable=True)
    eta = Column(Date, nullable=True)
    container_number = Column(String, nullable=True)
    container_size = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)
    payment_due_date = Column(Date, nullable=True)
    creditor = Column(String, nullable=True)
    invoice_num = Column(String, nullable=True)
    ar_ap = Column(String, nullable=True)
    is_post = Column(String, nullable=True)

    # Relationships
    # charges = relationship('DebitNoteCharges', backref='debit_note', cascade='all, delete-orphan')
    # invoiced_amount = relationship('DebitNoteAmount', foreign_keys='DebitNoteAmount.debit_note_id', uselist=False, cascade='all, delete-orphan')
    # balance_due = relationship('DebitNoteAmount', foreign_keys='DebitNoteAmount.debit_note_id', uselist=False, cascade='all, delete-orphan')

class DebitNoteEmail(Base):
    __tablename__ = 'debit_note_email'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(String, nullable=False, unique=True)
    subject = Column(String, nullable=False)
    file_name = Column(String, nullable=True)
    email_status_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.email_id,
            'subject': self.subject,
            'file_name': self.file_name,
            'email_status_id': self.email_status_id,
            'created_at': self.created_at.isoformat(),  # Convert datetime to string
            'updated_at': self.created_at.isoformat()  # Convert datetime to string
        }

    def to_json(self):
        return json.dumps(self.to_dict(), default=str)  # Convert dictionary to JSON string

class DebitNoteEmailStatus(Base):
    __tablename__ = 'debit_note_email_status'

    id = Column(Integer, primary_key=True, autoincrement=True)
    status_name = Column(Enum(DebitNoteEmailStatusEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

# Function to insert sample statuses
def insert_email_status():
    SessionLocal = DebitNoteDB.get_session_local()
    session = SessionLocal()
    try:
        statuses = [
            DebitNoteEmailStatus(id=1, status_name=DebitNoteEmailStatusEnum.CREATED, is_active=True),
            DebitNoteEmailStatus(id=2, status_name=DebitNoteEmailStatusEnum.PENDING_DATA_EXTRACTION, is_active=True),
            DebitNoteEmailStatus(id=3, status_name=DebitNoteEmailStatusEnum.FAILED, is_active=True),
            DebitNoteEmailStatus(id=4, status_name=DebitNoteEmailStatusEnum.READY_FOR_REVIEW, is_active=True),
            DebitNoteEmailStatus(id=5, status_name=DebitNoteEmailStatusEnum.PENDING_CW_UPLOAD, is_active=True),
            DebitNoteEmailStatus(id=6, status_name=DebitNoteEmailStatusEnum.SKIPPED, is_active=True),
            DebitNoteEmailStatus(id=7, status_name=DebitNoteEmailStatusEnum.DOWNLOADED, is_active=True),
        ]
        session.add_all(statuses)
        session.commit()
    finally:
        session.close()


# Create the table
def create_table():
    engine = DebitNoteDB.get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    if settings.FASTAPI_ENVIRONMENT == 'test':
        create_table()
    insert_email_status()
