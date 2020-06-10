from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship

from .database import Base


class Patient(Base):
    __tablename__ = "patient"
    patient_id = Column(Integer, primary_key=True)
    name = Column(String)
    sex = Column(String)
    age = Column(Integer)
    heart_rate_minima = Column(Integer)
    heart_rate_maxima = Column(Integer)
    spo2_minima = Column(Integer)
    systolic_bp_maxima = Column(Integer)
    diastolic_bp_maxima = Column(Integer)
    ward_number = Column(String)
    # children = relationship("BedDetails")


class BedDetails(Base):
    __tablename__ = "bedDetails"
    bed_id = Column(Integer, primary_key=True, autoincrement=True)
    bed_no = Column(Integer)
    ward_no = Column(String)
    # floor_number = Column(String)
    current_patient_id = Column(Integer, ForeignKey('patient.patient_id'))
    ip_address = Column(String)
    children = relationship("MedicalDetails")


class MedicalDetails(Base):
    __tablename__ = "medicData"
    id = Column(Integer, primary_key=True, autoincrement=True)
    bed_id = Column(Integer, ForeignKey('bedDetails.bed_id'))
    patient_id = Column(Integer, ForeignKey('patient.patient_id'))
    bed_no = Column(Integer)
    time = Column(DateTime)
    bpm_current = Column(Float)
    bpm_avg = Column(Float)
    bp_systolic_current = Column(Integer)
    bp_systolic_avg = Column(Integer)
    bp_diastolic_current = Column(Integer)
    bp_diastolic_avg = Column(Integer)
    spo2_current = Column(Integer)
    spo2_avg = Column(Integer)
