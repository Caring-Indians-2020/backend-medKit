import asyncio
import random
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any, List, Tuple

from asyncio_mqtt import Client, MqttError

BROKER_ADDRESS = "127.0.0.1"

DELAY_HR = 10
DELAY_SPO2 = 10
DELAY_BP = 60
DELAY_PPG = 10

# client = mqtt.Client("NODE_SIM")
# client.connect(broker_address, 1883, 60)
# client.publish("1_2/Details", "123478,Sharma,20,M")
# client.publish("1_1/Details", "124558,Saksham Sharma,20,M,15")
# client.publish("1_3/Details", "124558,Saksham Sharma,20,M,15")
# client.publish("1_1/Temp", "25,26.7")
# client.publish("1_1/HeartRate", "78.5,58.7")
# client.publish("1_1/SpO2", "80,78.8")
# client.publish("1_1/BP", "58,68")

# client.publish("1_2/Temp", "25,26.7")
# client.publish("1_2/HeartRate", "78.5,58.7")
# client.publish("1_2/SpO2", "80,78.8")
# client.publish("1_2/BP", "58,68")


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
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

async def startSim(beds: List[Tuple[str, str]]):
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
        task = asyncio.create_task(log_messages(messages, f'Other -- [topic="{{}}"] {{}}'))
        tasks.add(task)

        await client.subscribe('#') # subscribe to all messages

        for bed in beds:
            tasks.add(asyncio.create_task(onboardPatient(bed, client)))
            tasks.add(asyncio.create_task(startHRProducer(bed, client)))
            tasks.add(asyncio.create_task(startBPProducer(bed, client)))
            tasks.add(asyncio.create_task(startSpO2Producer(bed, client)))
        
        await asyncio.gather(*tasks)


async def onboardPatient(bed: Tuple[str, str], client: Client):
    wardNo, bedNo = bed
    topic = f'{wardNo}/{bedNo}/patientDetails'
    patientId = int(bedNo) * 1000
    bedDetails = (
        f"{patientId}",  # patient ID
        f"Patient_{patientId}",  # name
        random.randint(15, 99),  # age
        random.choice(['M', 'F', 'O']),  # gender
        random.randint(100, 105),  # sys_min
        random.randint(135, 145),  # sys_max
        random.randint(85, 93),  # spo2_min
        random.randint(50, 60),  # hr_min
        random.randint(130, 140),  # hr_max
        "127.0.0.1",  # ip_addr
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
        sys = getNextRandomInt(sys, 100, 200, 5)
        dia = getNextRandomInt(dia, 30, sys, 5)
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
    _beds = [
        ("W1", "1"),
        ("W1", "2"),
        ("W1", "3"),
        ("W1", "4"),
    ]
    asyncio.run(startSim(_beds))
