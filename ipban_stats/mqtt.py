import logging

import paho.mqtt.client as mqtt

_logger = logging.getLogger()


class Mqtt:
    def __init__(self, hostname, port=1883):
        self._mqtthost = hostname
        self._mqttport = port

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("$SYS/#")

    # The callback for when a PUBLISH message is received from the server.
    @staticmethod
    def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))

    def connect(self):
        _logger.info(f"Connecting to MQTT host '{self._mqtthost}:{self._mqttport}'")

        self.client.connect(self._mqtthost, self._mqttport, 60)
        self.client.loop_start()

    def publish(self, topic, value):
        _logger.debug("Publishing MQTT messaget host")
        self.client.publish(topic, value)
