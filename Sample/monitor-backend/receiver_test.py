from mqtt_receiver.receiver import MqttReceiver
from sql.models import Patient

# with open('hello.txt','w') as f:
#     pass
# pp = Patient(patient_id="hello", name="world", sex="M", age=1, heart_rate_maxima=2, heart_rate_minima=3, spo2_minima=4,
#              systolic_bp_maxima=5, systolic_bp_minima=6)

empty = Patient()
print(empty)
print(empty.systolic_bp_minima)
receiver = MqttReceiver()
# import paho.mqtt.client as mqtt
#
#
# # The callback for when the client receives a CONNACK response from the server.
# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code " + str(rc))
#
#     # Subscribing in on_connect() means that if we lose the connection and
#     # reconnect then subscriptions will be renewed.
#     client.subscribe("#")
#
#
# # The callback for when a PUBLISH message is received from the server.
# def on_message(client, userdata, msg):
#     print(msg.topic + " " + str(msg.payload))
#
#
# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message
#
# client.connect("127.0.0.1")
#
# # Blocking call that processes network traffic, dispatches callbacks and
# # handles reconnecting.
# # Other loop*() functions are available that give a threaded interface and a
# # manual interface.
# client.loop_forever()
