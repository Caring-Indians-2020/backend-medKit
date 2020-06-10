import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session

from sql import crud
from sql.database import SessionLocal, engine
from sql.models import Patient, MedicalDetails, BedDetails
from mqtt_receiver.constants import MedicalRecordType


class MqttReceiver:
    def __init__(self):
        self.broker_address = "127.0.0.1"
        self.cached_patient_data = {}
        self.engine = engine
        self.session: Session = SessionLocal
        self.client = mqtt.Client("baseStation")
        self.client.connect(self.broker_address, 1883, 60)
        self.client.subscribe("/*")
        self.client.on_message = self.add_data

    def add_data(self, payload):
        topic = str(payload.topic).split("/")
        ward_number = topic[0]
        bed_number = topic[1]
        parameter = topic[2]
        current_patient_data: MedicalDetails
        message = str(payload.payload.decode("utf-8")).split(",")
        if parameter == "patientDetails":
            self.add_patient_details(message, ward_number, bed_number)

        else:
            bed_ward_key = bed_number + ward_number
            if bed_ward_key in self.cached_patient_data:
                pass
            else:
                patient_medical_details: MedicalDetails = crud.update_patient_details(
                    self.session, ward_number, bed_number, parameter, message[0])
                self.cached_patient_data[bed_ward_key] = patient_medical_details

    def add_patient_details(self, message, ward_number, bed_number):
        patient = Patient(int(message[0]), message[1], message[3], int(message[2]), int(message[7]),
                          int(message[8]), int(message[6]), int(message[5]), int(message[4]),
                          ward_number)
        bed_details = BedDetails(bed_no=bed_number, ward_no=ward_number, current_patient_id=message[0],
                                 ip_address=message[9])
        crud.save_or_update_patient(self.session, patient)
        crud.update_or_add_bed_details(self.session, bed_details)


    # def update_patient_medical_records(self, ward_number, bed_number, record_type, details):
    #     if record_type == MedicalRecordType.SPO2.value:
    #         patient_details.spo2_current = record_parameter
    #         patient_details.spo2_avg = record_parameter
    #     if record_type == MedicalRecordType.DIASTOLIC_BP.value:
    #         patient_details.bp_diastolic_avg = record_parameter
    #         patient_details.bp_diastolic_current = record_parameter
    #     if record_type == MedicalRecordType.SYSTOLIC_BP.value:
    #         patient_details.bp_systolic_current = record_parameter
    #         patient_details.bp_systolic_avg = record_parameter
    #     if record_type == MedicalRecordType.HEART_RATE.value:
    #         patient_details.bpm_current = record_parameter
    #         patient_details.bpm_avg = record_parameter
