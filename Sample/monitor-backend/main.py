import asyncio
import random
import traceback
import uvicorn
import time

from fastapi import Depends, FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse

from mqtt_receiver.constants import html
from sql import crud, models, response
from sql.database import SessionLocal, engine
from mqtt_receiver.receiver import MqttReceiver


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
receiver = None


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        traceback.print_exc()
        return Response("Internal server error", status_code=500)


app.middleware('http')(catch_exceptions_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# startup : start mqtt receiver


@app.on_event("startup")
def startup_event():
    global receiver
    print('Starting mqtt client')
    receiver = MqttReceiver()

# Dependency


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# t1 = threading.Thread(target=start_receiver).start()
# if __name__ == '__main__':
#     t2 = threading.Thread(target=start_api).start()
#     # Process(target=start_receiver).start()
#     # Process(target=start_api).start()


# @app.post("/patient/create", response_model=schemas.Patient, description="Create a new patient")
# def create_patient(patient: schemas.Patient, db: Session = Depends(get_db)):
#     db_user = crud.get_patient_by_id(db, id=patient.patient_id)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Patient already registered")
#     return crud.create_user(db=db, patient=patient)
#

@app.delete("/patients/delete", response_model=str)
def delete_patient(id: str, db: Session = Depends(get_db)):
    all_patients = crud.delete_patient_by_id(db, id)
    return all_patients


@app.get("/beds/{bed_id}", description="Get Details of a Bed")
def get_bed_details(bed_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_bed_details_by_id(db, bed_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return response.BedResponse(db_user[0], db_user[1], db_user[2])


@app.get("/beds", description="Get All Beds")
def get_all_bed_details(ward_number: str = None, db: Session = Depends(get_db)):
    all_beds_details = crud.get_all_bed_details(db, ward_number)
    if all_beds_details is None:
        raise HTTPException(status_code=404, detail="No Beds found")
    details = []
    for bed in all_beds_details:
        details.append(response.BedResponse(bed[0], bed[1], bed[2]))
    return details


def generate_random():
    return [round(random.uniform(30, 150), 2), round(random.uniform(30, 150), 2)]


def generate_sample_data():
    return {'123458': {'temp': generate_random(), 'heartRate': generate_random(), 'SpO2': generate_random(),
                       'BP': generate_random()}}


async def subscribe_realtime(bed_id: int, ws: WebSocket, db: Session):
    global receiver
    async def ws_send(data):
        await ws.send_json(data)
    wsId = str(time.time())
    bed: models.BedDetails = crud.get_bed(db, bed_id)
    cacheKey = f'{bed.bed_no}_{bed.ward_no}'
    # simulate an endless series of messages from the mqtt topic
    while True:
        rtd = response.MedicDataRealtime()
        dataByBedPpg = receiver.cached_PPG_data.get(cacheKey)
        dataByBedEcg = receiver.cached_ECG_data.get(cacheKey)
        print(f'receiver.cached_PPG_data = {receiver.cached_PPG_data}')
        print(f'receiver.cached_ECG_data = {receiver.cached_ECG_data}')

        if dataByBedPpg is not None:

            if wsId not in dataByBedPpg:
                dataByBedPpg[wsId] = []
            # get cached data
            rtd.ppg = dataByBedPpg[wsId]
            receiver.cached_PPG_data[cacheKey][wsId] = []
        if dataByBedEcg is not None:

            if wsId not in dataByBedEcg:
                dataByBedEcg[wsId] = []
            rtd.ecg = dataByBedEcg[wsId]
            receiver.cached_ECG_data[cacheKey][wsId] = []

        try:
            print("sending data")
            print(rtd.__dict__)
            await ws_send(rtd.__dict__)
        except:
            print(f"ws disconnected for bed id = {bed_id}")
            break
        await asyncio.sleep(0.5)
    if receiver.cached_ECG_data.get(cacheKey) is not None and wsId in receiver.cached_ECG_data.get(cacheKey):
        print(f'clearing ECG cache for {wsId}')
        del receiver.cached_ECG_data.get(cacheKey)[wsId]
    if receiver.cached_ECG_data.get(cacheKey) is not None and wsId in receiver.cached_ECG_data.get(cacheKey):
        print(f'clearing PPG cache for {wsId}')
        del receiver.cached_ECG_data.get(cacheKey)[wsId]


@app.websocket("/beds/{bed_id}/realtime")
async def websocket_endpoint(websocket: WebSocket, bed_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    print(f"ws connected for bed id = {bed_id}")
    await subscribe_realtime(bed_id, websocket, db)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
