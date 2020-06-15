from enum import Enum


class MedicalRecordType(Enum):
    SPO2 = "spO2"
    DIASTOLIC_BP = "diaBP"
    SYSTOLIC_BP = "sysBP"
    PPG = "ppg"
    HEART_RATE = "HR"
