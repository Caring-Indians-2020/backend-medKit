import asyncio
import random
import time
import traceback
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any, List, Tuple

import requests
import uvicorn
from asyncio_mqtt import Client, MqttError
from fastapi import BackgroundTasks, FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import Response

BROKER_ADDRESS = "127.0.0.1"
SERVER_PORT = 8082

DELAY_HR = 10
DELAY_SPO2 = 10
DELAY_BP = 60
DELAY_PPG = 10

app = FastAPI()


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

client: Client
stack: AsyncExitStack


@app.post("/")
async def update_patient(
    request: Request,
        pID: str = Form(...),
        pName: str = Form(...),
        pGender: str = Form(...),
        pAge: int = Form(...),
        pMinHR: int = Form(...),
        pMaxHR: int = Form(...),
        pMinspO2: int = Form(...),
        pMaxSysBP: int = Form(...),
        pMinSysBP: int = Form(...),
        pBedNo: str = Form(...),
        pWardNo: str = Form(...),
):
    global client
    # need to publish a message that patient details have been updated
    await onboardPatient((pWardNo, pBedNo), client, (
        pID,
        pName,
        pGender,
        pAge,
        pMinSysBP,
        pMaxSysBP,
        pMinspO2,
        pMinHR,
        pMaxHR,
        f'{request.url.netloc}'
    ))

# @app.get("/startup")
# async def scheduleSimStart(background_tasks: BackgroundTasks):
#     background_tasks.add_task(startSim)


@app.on_event("startup")
async def scheduleSimStart():
    asyncio.ensure_future(startSim())

@app.on_event("shutdown")
async def shutdownSim():
    global stack
    print('Shutting down...')
    await stack.aclose()

####################
####  SIM Code  ####
####################

def getNextRandomInt(old: int, lo: int, hi: int, delta: int):
    ub = min(old + delta, hi)
    lb = max(old - delta, lo)
    return random.randint(lb, ub)


def getNextRandomFloat(old: float, lo: float, hi: float, delta: float):
    ub = min(old + delta, hi)
    lb = max(old - delta, lo)
    return round(random.uniform(lb, ub), 2)


async def publicMessage(client: Client, topic: str, message: Any):

    await client.publish(topic, ",".join(message), qos=1)


async def log_messages(messages, template):
    async for message in messages:
        print(template.format(message.topic, message.payload.decode()))


async def cancel_tasks(tasks):
    print('Cancelling tasks')
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

async def startSim():
    global client, stack
    # change entries to modify test
    beds = [
        ("W1", "1"),
        ("W1", "2"),
        ("W1", "3"),
        ("W1", "4"),
    ]
    async with AsyncExitStack() as stack:
        # Connect to the MQTT broker
        client = Client(BROKER_ADDRESS)
        await stack.enter_async_context(client)

        tasks = set()
        stack.push_async_callback(cancel_tasks, tasks)

        outbound_topics = [
            "+/+/patientDetails",
            "+/+/HR",
            "+/+/spO2",
            "+/+/diaBP",
            "+/+/sysBP",
            "+/+/ppg",
            "+/+/ecg",
        ]
        for ot in outbound_topics:
            manager = client.filtered_messages(ot)
            messages = await stack.enter_async_context(manager)
            template = f'Outbound -- [topic="{{}}"] {{}}'
            task = asyncio.create_task(log_messages(messages, template))
            tasks.add(task)

        inbound_topics = [
            "+/+/sendDetails"
        ]

        for it in inbound_topics:
            manager = client.filtered_messages(it)
            messages = await stack.enter_async_context(manager)
            template = f'Inbound -- [topic="{{}}"] {{}}'
            task = asyncio.create_task(log_messages(messages, template))
            tasks.add(task)

        # Messages that doesn't match a filter will get logged here
        messages = await stack.enter_async_context(client.unfiltered_messages())
        task = asyncio.create_task(log_messages(
            messages, f'Other -- [topic="{{}}"] {{}}'))
        tasks.add(task)

        await client.subscribe('#')  # subscribe to all messages

        for bed in beds:
            tasks.add(asyncio.create_task(onboardPatient(bed, client)))
            tasks.add(asyncio.create_task(startHRProducer(bed, client)))
            tasks.add(asyncio.create_task(startBPProducer(bed, client)))
            tasks.add(asyncio.create_task(startSpO2Producer(bed, client)))
        await asyncio.gather(*tasks)


async def onboardPatient(bed: Tuple[str, str], client: Client, bedDetails=None):
    wardNo, bedNo = bed
    topic = f'{wardNo}/{bedNo}/patientDetails'
    patientId = name = age = gender = ''
    if random.randint(1, 100) > 5:
        patientId = f"{int(bedNo) * 1000}"
        name = f"Patient_{patientId}"
        gender = random.choice(['M', 'F', 'O'])
        age = random.randint(15, 99)
    if bedDetails is None:
        bedDetails = (
            patientId,  # patient ID
            name,  # name
            gender,  # gender
            age,  # age
            random.randint(88, 92),  # sys_min
            random.randint(135, 145),  # sys_max
            random.randint(85, 93),  # spo2_min
            random.randint(50, 60),  # hr_min
            random.randint(130, 140),  # hr_max
            f"127.0.0.1:{SERVER_PORT}",  # ip_addr
        )
    await client.publish(topic, ",".join(map(str, bedDetails)), qos=1)


async def startHRProducer(bed: Tuple[str, str], client: Client):
    wardNo, bedNo = bed
    topic = f'{wardNo}/{bedNo}/HR'
    hr = 70
    while True:
        hr = getNextRandomInt(hr, 30, 150, 5)
        await client.publish(topic, hr, qos=1)
        await asyncio.sleep(DELAY_HR)


async def startBPProducer(bed: Tuple[str, str], client: Client):
    wardNo, bedNo = bed
    topic1 = f'{wardNo}/{bedNo}/diaBP'
    topic2 = f'{wardNo}/{bedNo}/sysBP'
    sys = 110
    dia = 70
    while True:
        sys = getNextRandomInt(sys, 80, 200, 5)
        dia = getNextRandomInt(dia, 50, sys, 5)
        await client.publish(topic1, dia, qos=1)
        await client.publish(topic2, sys, qos=1)
        await asyncio.sleep(DELAY_BP)


async def startSpO2Producer(bed: Tuple[str, str], client: Client):
    wardNo, bedNo = bed
    topic1 = f'{wardNo}/{bedNo}/spO2'
    topic2 = f'{wardNo}/{bedNo}/ppg'
    seed = 98
    while True:
        ppg = []
        for i in range(100):
            seed = getNextRandomInt(seed, 50, 100, 1)
            ppg.append(str(seed))
        await client.publish(topic1, seed, qos=1)
        await client.publish(topic2, ",".join(ppg), qos=1)
        await asyncio.sleep(DELAY_SPO2)


if __name__ == "__main__":
    uvicorn.run("nodeSim:app", port=SERVER_PORT, reload=True)
