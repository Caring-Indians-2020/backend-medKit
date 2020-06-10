from typing import List
from .models import Patient, MedicalDetails, BedDetails


class BedResponse:
    patientId: str
    name: str
    age: int
    sex: str
    bedNo: str
    ipAddress: str
    wardNo: str
    bedId: str
    time: str
    heartRateMinima: int
    heartRateMaxima: int
    spO2Minima: int
    systolicBPMaxima: int
    systolicBPMinima: int
    bpmCurrent: int
    bpmAvg: int
    bpSystolicCurrent: int
    bpSystolicAvg: int
    bpDiastolicCurrent: int
    bpDiastolicAvg: int
    spO2Current: int
    spO2Avg: int
    qtCurrent: int
    qtAvg: int
    rrCurrent: int
    rrAvg: int

    def __init__(self, bed_details: BedDetails, patient_details: Patient, medical_details: MedicalDetails):
        if patient_details is not None:
            self.patientId = patient_details.patient_id
            self.name = patient_details.name
            self.age = patient_details.age
            self.sex = patient_details.sex
            self.heartRateMaxima = patient_details.heart_rate_maxima
            self.heartRateMinima = patient_details.heart_rate_minima
            self.spO2Minima = patient_details.spo2_minima
            self.systolicBPMinima = patient_details.systolic_bp_minima
            self.systolicBPMaxima = patient_details.systolic_bp_maxima

        if bed_details is not None:
            self.bedNo = str(bed_details.bed_no)
            self.ipAddress = bed_details.ip_address
            self.wardNo = bed_details.ward_no
            self.bedId = str(bed_details.bed_id)

        if medical_details is not None:
            self.time = str(medical_details.time)
            self.bpmCurrent = medical_details.bpm_current
            self.bpmAvg = medical_details.bpm_avg
            self.bpSystolicCurrent = medical_details.bp_systolic_current
            self.bpSystolicAvg = medical_details.bp_systolic_avg
            self.bpDiastolicCurrent = medical_details.bp_diastolic_current
            self.bpDiastolicAvg = medical_details.bp_diastolic_avg
            self.spO2Current = medical_details.spo2_current
            self.spO2Avg = medical_details.spo2_avg
            self.qtAvg = medical_details.qt_avg
            self.qtCurrent = medical_details.qt_current
            self.rrAvg = medical_details.rr_avg
            self.rrCurrent = medical_details.rr_current


class MedicDataRealtime:
    ppg: List[int]
    ecg: List[int]
