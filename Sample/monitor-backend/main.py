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


async def subscribe_realtime(bed_id: int, ws: WebSocket):
    async def ws_send(data):
        await ws.send_json(data)
    wsId = str(time.time)
    bed = crud.get_bed(bed_id)
    # simulate an endless series of messages from the mqtt topic
    while True:
        dataByBed = receiver.cachedData[f'{bed.bedNo+"_"+bed.wardNo}']
        if dataByBed is not None:
            rtd = response.MedicDataRealtime()
            if wsId not in dataByBed:
                dataByBed[wsId] = []
            rtd.ppg = dataByBed[wsId]
            receiver.cachedData[f'{bed.bedNo+"_"+bed.wardNo}'][wsId] = None
            # # sending a list of 10 values
            #     random.randrange(1, 100),
            #     random.randrange(1, 100),
            #     random.randrange(1, 100),
            #     random.randrange(1, 100),
            #     random.randrange(1, 100),
            #     random.randrange(1, 100),
            #     random.randrange(1, 100),
            #     random.randrange(1, 100),
            #     random.randrange(1, 100),
            #     random.randrange(1, 100)
            # ]
            try:
                await ws_send(rtd.__dict__)
            except:
                print(f"ws disconnected for bed id = {bed_id}")
                return
        await asyncio.sleep(0.5)


@app.websocket("/beds/{bed_id}/realtime")
async def websocket_endpoint(websocket: WebSocket, bed_id: int):
    await websocket.accept()
    print(f"ws connected for bed id = {bed_id}")
    await subscribe_realtime(bed_id, websocket)


if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", reload=True)