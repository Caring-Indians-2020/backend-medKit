from .models import Patient, MedicalDetails, BedDetails


class BedResponse:
    id: int
    name: str
    age: int
    sex: str
    floorNumber: str
    bedNo: str
    ipAddress: str
    wardNo: str
    bedId: str
    time: str
    heartRateMinima: float
    heartRateMaxima: float
    spO2Minima: float
    systolicBPMaxima: float
    diastolicBPMaxima: float
    tempCurrent: float
    tempAvg: float
    bpmCurrent: float
    bpmAvg: float
    bpSystolicCurrent: float
    bpSystolicAvg: float
    bpDiastolicCurrent: float
    bpDiastolicAvg: float
    spO2Current: float
    spO2Avg: float

    def __init__(self, bed_details: BedDetails, patient_details: Patient, medical_details: MedicalDetails):
        self.id = patient_details.patient_id
        self.name = patient_details.name
        self.age = patient_details.age
        self.sex = patient_details.sex
        self.floorNumber = bed_details.floor_number
        self.bedNo = str(bed_details.bed_no)
        self.ip_address = bed_details.ip_address
        self.ward_no = bed_details.ward_no
        self.bed_id = str(bed_details.bed_id)
        self.time = str(medical_details.time)
        self.heartRateMaxima = patient_details.heart_rate_maxima
        self.heartRateMinima = patient_details.heart_rate_minima
        self.spO2Minima = patient_details.spo2_minima
        self.diastolicBPMaxima = patient_details.diastolic_bp_maxima
        self.systolicBPMaxima = patient_details.systolic_bp_maxima
        self.tempCurrent = medical_details.temp_current
        self.tempAvg = medical_details.temp_avg
        self.bpmCurrent = medical_details.bpm_current
        self.bpmAvg = medical_details.bpm_avg
        self.bpSystolicCurrent = medical_details.bp_systolic_current
        self.bpSystolicAvg = medical_details.bp_systolic_avg
        self.bpDiastolicCurrent = medical_details.bp_diastolic_current
        self.bpDiastolicAvg = medical_details.bp_diastolic_avg
        self.spO2Current = medical_details.spo2_current
        self.spO2Avg = medical_details.spo2_avg
