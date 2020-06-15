import datetime
import os

import paho.mqtt.client as mqtt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from mqtt_receiver.constants import MedicalRecordType
from sql import crud
from sql.database import engine, Base
from sql.models import Patient, MedicalDetails, BedDetails


class MqttReceiver:
    def __init__(self):
        self.broker_address = "127.0.0.1"
        self.cached_patient_data = {}
        SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.dirname(os.path.realpath(__file__))}/../patientInfo.db"
        self.engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
        # Base = declarative_base()
        Base.metadata.create_all(bind=engine)

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        self.session: Session = SessionLocal()

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        # self.client.subscribe("/*")
        self.client.on_message = self.add_data

        self.client.connect(self.broker_address)
        self.client.loop_forever()
        # while True:
        #     self.client.loop()
        #     self.client.on_message = self.add_data
        # with open('hello.txt','w') as f:
        #     pass

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.client.subscribe("#")

    def add_data(self, client, userdata, payload):
        topic = str(payload.topic).split("/")
        # print("here")
        # print(payload.topic + " " + str(payload.payload))
        ward_number = topic[0]
        bed_number = topic[1]
        parameter = topic[2]
        current_patient_data: MedicalDetails
        message = str(payload.payload.decode("utf-8")).split(",")
        if parameter == "patientDetails":
            print("patient_details_reached")
            self.add_patient_details(message, ward_number, bed_number)

        else:
            # bed_ward_key = bed_number + ward_number
            # if bed_ward_key in self.cached_patient_data:
            #     pass
            # else:
            patient_medical_details: MedicalDetails = self.update_patient_medical_records(ward_number, bed_number,
                                                                                              parameter, message[0])
            # self.cached_patient_data[bed_ward_key] = patient_medical_details

    def add_patient_details(self, message, ward_number, bed_number):
        patient = Patient(patient_id=message[0], name=message[1], sex=message[2], age=int(message[3]),
                          heart_rate_minima=int(message[4]),
                          heart_rate_maxima=int(message[5]), spo2_minima=int(message[6]),
                          systolic_bp_maxima=int(message[7]), systolic_bp_minima=int(message[8]))

        bed_details = BedDetails(bed_no=bed_number, ward_no=ward_number, current_patient_id=message[0],
                                 ip_address=message[9])
        crud.save_or_update_patient(self.session, patient)
        crud.update_or_add_bed_details(self.session, bed_details)

    def get_or_create_patient_medical_details(self, ward_number, bed_number):
        patient_medical_details = crud.get_patient_details(self.session, ward_number, bed_number)
        return patient_medical_details

    def update_patient_medical_records(self, ward_number, bed_number, record_type, record_value):
        patient_details = None
        bed_ward_key = bed_number + ward_number
        if bed_ward_key in self.cached_patient_data:
            patient_details = self.cached_patient_data[bed_ward_key]
        else:
            patient_details = self.get_or_create_patient_medical_details(ward_number, bed_number)
        if record_type == MedicalRecordType.SPO2.value:
            patient_details.spo2_current = record_value
            patient_details.spo2_avg = record_value
            patient_details.time = datetime.datetime.now()
        if record_type == MedicalRecordType.DIASTOLIC_BP.value:
            patient_details.bp_diastolic_avg = record_value
            patient_details.bp_diastolic_current = record_value
            patient_details.time = datetime.datetime.now()
        if record_type == MedicalRecordType.SYSTOLIC_BP.value:
            patient_details.bp_systolic_current = record_value
            patient_details.bp_systolic_avg = record_value
            patient_details.time = datetime.datetime.now()
        if record_type == MedicalRecordType.HEART_RATE.value:
            patient_details.bpm_current = record_value
            patient_details.bpm_avg = record_value
            patient_details.time = datetime.datetime.now()
        details = crud.update_given_patient_details(self.session, patient_details)
        self.cached_patient_data[bed_ward_key] = details
        return details
