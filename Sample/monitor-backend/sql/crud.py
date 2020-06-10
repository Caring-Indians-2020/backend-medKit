from sqlalchemy import and_
from sqlalchemy.orm import Session

from mqtt_receiver.constants import MedicalRecordType
from .models import Patient, MedicalDetails, BedDetails


def get_bed_details_by_id(db: Session, bed_id: str):
    return db.query(BedDetails, Patient, MedicalDetails).join(Patient,
                                                              Patient.patient_id == BedDetails.current_patient_id).join(
        MedicalDetails, BedDetails.current_patient_id == MedicalDetails.patient_id).filter(
        BedDetails.bed_id == bed_id).first()


def is_patient_registered(db: Session, patient_id):
    if db.query(Patient).filter(Patient.patient_id == patient_id).first() is None:
        return False
    return True


def update_patient_details(db: Session, ward_number, bed_number, record_type, record_parameter):
    patient_bed = db.query(BedDetails).filter(
        and_(BedDetails.bed_no == bed_number, BedDetails.ward_no == ward_number)).first()
    patient_id = patient_bed["current_patient_id"]

    patient_details: MedicalDetails = db.query(MedicalDetails).filter(MedicalDetails.patient_id == patient_id).first()

    if record_type == MedicalRecordType.SPO2.value:
        patient_details.spo2_current = record_parameter
        patient_details.spo2_avg = record_parameter
    if record_type == MedicalRecordType.DIASTOLIC_BP.value:
        patient_details.bp_diastolic_avg = record_parameter
        patient_details.bp_diastolic_current = record_parameter
    if record_type == MedicalRecordType.SYSTOLIC_BP.value:
        patient_details.bp_systolic_current = record_parameter
        patient_details.bp_systolic_avg = record_parameter
    if record_type == MedicalRecordType.HEART_RATE.value:
        patient_details.bpm_current = record_parameter
        patient_details.bpm_avg = record_parameter
    db.commit()
    db.refresh(patient_details)
    return patient_details


# def create_user(db: Session, patient: schemas.Patient):
#     db_user = models.Patient(patient_id=patient.patient_id, name=patient.name, sex=patient.sex, age=patient.age)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# Sort by medical details id and select first
def get_all_bed_details(db: Session, ward_number: str):
    qry = db.query(BedDetails, Patient, MedicalDetails).outerjoin(Patient,
                                                                  Patient.patient_id == BedDetails.current_patient_id).outerjoin(
        MedicalDetails, BedDetails.current_patient_id == MedicalDetails.patient_id)

    if ward_number is not None:
        qry = qry.filter(BedDetails.ward_no == ward_number)
    return qry.all()


def delete_patient_by_id(db: Session, id: str):
    by_id = get_bed_details_by_id(db, id)
    try:
        db.delete(by_id)
        db.commit()
        return "Patient Deleted Successfully"
    except:
        return "Patient Not Found"


# Add or replace patient
def save_or_update_patient(db: Session, patient: Patient):
    if db.query(Patient).filter(Patient.patient_id == patient.patient_id).first() is None:
        db.add(patient)
        db.commit()
    else:
        pass
        # Add logic to update patient details


def update_or_add_bed_details(session: Session, bed_details: BedDetails):
    details: BedDetails = session.query(BedDetails).filter(BedDetails.bed_no == bed_details.bed_no).first()
    if details is None:
        session.add(bed_details)
        session.commit()
    else:
        details.current_patient_id = bed_details.current_patient_id
        details.ip_address = bed_details.ip_address
        session.commit()
