# from pydantic import BaseModel
#
#
# class Patient(BaseModel):
#     patient_id: int
#     name: str
#     age: int
#     sex: str
#
#     class Config:
#         orm_mode = True
#
#
# class PatientResponse:
#     id: int
#     Name: str
#     BedNo: int
#     Age: int
#     Sex: str
#     Time = str
#     tempCurrent = float
#     tempAvg = float
#     bpmCurrent = float
#     bpmAvg = float
#     bpCurrent = float
#     bpAvg = float
#     spO2Current = float
#     spO2Avg = float
#
#     def __init__(self, info, details):
#         self.id = info.id
#         self.Name = info.Name
#         self.BedNo = info.BedNo
#         self.Age = info.Age
#         self.Sex = info.Sex
#         self.Time = details.Time
#         self.tempCurrent = details.tempCurrent
#         self.tempAvg = details.tempAvg
#         self.bpmCurrent = details.bpmCurrent
#         self.bpmAvg = details.bpmAvg
#         self.bpCurrent = details.bpCurrent
#         self.bpAvg = details.bpmAvg
#         self.spO2Current = details.spO2Current
#         self.spO2Avg = details.spO2Avg
