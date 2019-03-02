import logging

import paho.mqtt.client as mqtt

_logger = logging.getLogger(__name__)


class Mqtt:
    def __init__(self, hostname, port=1883):
        self._mqtthost = hostname
        self._mqttport = port

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        # self.client.on_message = self.on_message

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        logging.info("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("$SYS/#")

    def connect(self):
        _logger.info(f"Connecting to MQTT host '{self._mqtthost}:{self._mqttport}'")

        self.client.connect(self._mqtthost, self._mqttport, 60)
        self.client.loop_start()

    def publish(self, topic, value):
        _logger.debug(f"Publishing MQTT message to topic '{topic}' with value '{value}'")
        self.client.publish(topic, value)
