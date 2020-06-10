from enum import Enum


class MedicalRecordType(Enum):
    SPO2 = "spO2"
    DIASTOLIC_BP = "diaBp"
    SYSTOLIC_BP = "sysBp"
    PPG = "ppg"
    HEART_RATE = "HR"
