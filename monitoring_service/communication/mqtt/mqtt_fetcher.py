# communication/mqtt_fetcher.py
import paho.mqtt.client as mqtt
import json

class MQTTFetcher:
    def __init__(self, broker, port, topic, core_manager):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.core_manager = core_manager
        self.client = mqtt.Client()
        self.client.on_message = self.on_message

    def on_message(self, client, userdata, msg):
        payload = json.loads(msg.payload.decode())
        self.core_manager.process_message(payload)

    def start(self):
        self.client.connect(self.broker, self.port)
        self.client.subscribe(self.topic)
        self.client.loop_start() # Esegue in un thread separato