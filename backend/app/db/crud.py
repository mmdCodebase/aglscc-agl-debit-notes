from .database import DebitNoteDB
from .model import DebitNoteEmail, DebitNote, DebitNoteCharges
from ..model.debit_notes import DebitNote as DebitNotePyDantic
from sqlalchemy import select, func, case
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class DebitNoteEmailCRUD:
    @staticmethod
    def create_entry(email_id, subject, file_name, email_status_id):
        SessionLocal = DebitNoteDB.get_session_local()
        session = SessionLocal()
        try:
            new_entry = DebitNoteEmail(
                email_id=email_id,
                subject=subject,
                file_name=file_name,
                email_status_id=email_status_id,
            )
            session.add(new_entry)
            session.commit()
            return new_entry
        finally:
            session.close()

    @staticmethod
    def get_all_email_status(email_status_id):
        SessionLocal = DebitNoteDB.get_session_local()
        session = SessionLocal()
        try:
            entry = (
                session.query(DebitNoteEmail)
                .filter(DebitNoteEmail.email_status_id == email_status_id)
                .all()
            )
            return entry
        finally:
            session.close()

    @staticmethod
    def read_entry(entry_id):
        SessionLocal = DebitNoteDB.get_session_local()
        session = SessionLocal()
        try:
            entry = (
                session.query(DebitNoteEmail)
                .filter(DebitNoteEmail.id == entry_id)
                .first()
            )
            return entry
        finally:
            session.close()

    @staticmethod
    def read_entry_by_status_id(status_id: int):
        SessionLocal = DebitNoteDB.get_session_local()
        session = SessionLocal()
        try:
            entry = (
                session.query(DebitNoteEmail)
                .filter(DebitNoteEmail.email_status_id == status_id)
                #.filter(DebitNoteEmail.email_id == 'AAMkADlkYzYxMmE0LTJmNDUtNDk2NC04YTBlLTE3Nzk4MGM3MjJiNgBGAAAAAADq4lOoiq4-RK6EKpDIFMwIBwBxIJJ_YUZoQJCtwNJF1C14AAAAAAEMAABxIJJ_YUZoQJCtwNJF1C14AAIM-nz1AAA=')
                .order_by(DebitNoteEmail.created_at.desc())
                .all()
            )
            return entry
        finally:
            session.close()
    
    @staticmethod
    def read_entry_by_email_id(email_id: str):
        SessionLocal = DebitNoteDB.get_session_local()
        session = SessionLocal()
        try:
            entry = (
                session.query(DebitNoteEmail)
                .filter(DebitNoteEmail.email_id == email_id)
                .order_by(DebitNoteEmail.created_at.desc())
                .all()
            )
            return entry
        finally:
            session.close()

    @staticmethod
    def update_entry(email_id, subject=None, file_name=None, email_status_id=None):
        SessionLocal = DebitNoteDB.get_session_local()
        session = SessionLocal()
        try:
            entry = (
                session.query(DebitNoteEmail)
                .filter(DebitNoteEmail.email_id == email_id)
                .first()
            )
            if entry:
                if subject:
                    entry.subject = subject
                if file_name:
                    entry.file_name = file_name
                if email_status_id:
                    entry.email_status_id = email_status_id
                entry.updated_at = datetime.now(timezone.utc)
                session.commit()
            return entry
        finally:
            session.close()

    @staticmethod
    def delete_entry(entry_id):
        SessionLocal = DebitNoteDB.get_session_local()
        session = SessionLocal()
        try:
            entry = session.query(MyTable).filter(MyTable.id == entry_id).first()
            if entry:
                session.delete(entry)
                session.commit()
            return entry
        finally:
            session.close()


class DebitNoteCRUD:
    @staticmethod
    def insert_debit_note(debit_note: DebitNotePyDantic):
        SessionLocal = DebitNoteDB.get_session_local()
        session = SessionLocal()
        try:
            debit_note_dict = debit_note.dict()
            del debit_note_dict["charges"]
            del debit_note_dict["invoiced_amount"]
            del debit_note_dict["balance_due"]
            new_debit_note = DebitNote(**debit_note_dict)
            session.add(new_debit_note)
            session.commit()
            return new_debit_note.id
        finally:
            session.close()

    @staticmethod
    def insert_debit_note_charges(debit_note_id, debit_note: DebitNotePyDantic):
        SessionLocal = DebitNoteDB.get_session_local()
        session = SessionLocal()
        try:
            new_debit_note_charges = debit_note.charges
            for new_debit_note_charge in new_debit_note_charges:
                new_debit_note_charge = DebitNoteCharges(
                    debit_note_id=debit_note_id, **new_debit_note_charge.dict()
                )
                session.add(new_debit_note_charge)
            session.commit()
            return len(new_debit_note_charges)
        finally:
            session.close()
            
    @staticmethod
    def insert_debit_note_charge(debit_note_id, debit_note_charge: DebitNoteCharges):
        SessionLocal = DebitNoteDB.get_session_local()
        session = SessionLocal()
        try:
            new_debit_note_charge = DebitNoteCharges(
                debit_note_id=debit_note_id, **debit_note_charge.dict()
            )
            logger.info(new_debit_note_charge)
            session.add(new_debit_note_charge)
            session.commit()
            return True
        finally:
            session.close()

    @staticmethod
    def get_debit_note_by_file_name(file_name: str):
        SessionLocal = DebitNoteDB.get_session_local()
        session = SessionLocal()
        query = (
            session.query(
                DebitNote.agl_shipment_number,
                DebitNote.debit_note_number.label("supplier_cost_ref"),
                DebitNote.invoice_date,
                DebitNote.creditor,
                DebitNote.id.label("debit_note_id"),
                DebitNoteEmail.file_name,
                DebitNoteEmail.subject,
                DebitNoteEmail.email_id
            )
            .join(
                DebitNoteEmail,
                DebitNote.email_id == DebitNoteEmail.email_id,
                isouter=True,
            )
            .filter(DebitNoteEmail.file_name == file_name)
        )
        return query.first()

    @staticmethod
    def get_charges_by_debit_note_id(debit_note_id: int):
        SessionLocal = DebitNoteDB.get_session_local()
        session = SessionLocal()
        query = session.query(
            DebitNoteCharges.id,
            DebitNoteCharges.charge_code,
            DebitNoteCharges.description,
            DebitNoteCharges.charges_in_usd,
        ).filter(DebitNoteCharges.debit_note_id == debit_note_id)
        return query.all()

    @staticmethod
    def update_debit_note_by_id(debit_note_id: int, update_data: dict):
        SessionLocal = DebitNoteDB.get_session_local()
        session = SessionLocal()
        try:
            query = session.query(DebitNote).filter(DebitNote.id == debit_note_id)
            query.update(update_data)
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def update_charges_by_charge_id(charge_id: int, update_data: dict):
        SessionLocal = DebitNoteDB.get_session_local()
        session = SessionLocal()
        try:
            query = session.query(DebitNoteCharges).filter(
                DebitNoteCharges.id == charge_id
            )
            query.update(update_data)
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def get_charges_by_email_status_id_cw(email_status_id: int):
        SessionLocal = DebitNoteDB.get_session_local()
        session = SessionLocal()
        try:
            query = (
                select(
                    DebitNote.email_id,
                    DebitNote.agl_shipment_number,
                    DebitNote.creditor,
                    DebitNote.invoice_num,
                    None,  # DebitNote.invoice_date,
                    DebitNote.debit_note_number.label("supplier_cost_ref"),
                    DebitNote.ar_ap,
                    DebitNote.is_post,
                    DebitNoteEmail.updated_at,
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "FRT",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("FRT"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "AGEN",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("AGEN"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "AMS",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("AMS"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "EQUIP",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("EQUIP"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "ORIGIN",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("ORIGIN"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "LOCAL",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("LOCAL"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "PP",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("PP"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "TERFEE",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("TERFEE"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "TELEX",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("TELEX"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "VGM",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("VGM"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "DCART",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("DCART"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "SEAL",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("SEAL"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "DOC",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("DOC"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "BOOK",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("BOOK"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "CCLR",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("CCLR"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "ALINE",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("ALINE"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "PSEC",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("PSEC"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "EGF",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("EGF"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "TRANS",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("TRANS"),
                    func.sum(
                        case(
                            (
                                DebitNoteCharges.charge_code == "CHRENT",
                                DebitNoteCharges.charges_in_usd,
                            ),
                            else_=0,
                        )
                    ).label("CHRENT"),
                )
                .select_from(DebitNoteEmail)
                .join(DebitNote, DebitNoteEmail.email_id == DebitNote.email_id)
                .outerjoin(
                    DebitNoteCharges, DebitNote.id == DebitNoteCharges.debit_note_id
                )
                .where(DebitNoteEmail.email_status_id == email_status_id)
                .group_by(
                    DebitNote.email_id,
                    DebitNote.agl_shipment_number,
                    DebitNote.creditor,
                    DebitNote.invoice_num,
                    DebitNote.invoice_date,
                    DebitNote.debit_note_number,
                    DebitNote.ar_ap,
                    DebitNote.is_post,
                    DebitNoteEmail.updated_at,
                )
            )
            result = session.execute(query)
            return result.all()
        except Exception as e:
            # Handle any exceptions that may occur during the query execution
            print(f"An error occurred: {str(e)}")
            return None
        finally:
            session.close()


email_crud = DebitNoteEmailCRUD()
debit_note_crud = DebitNoteCRUD()
