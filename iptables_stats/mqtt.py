import logging

import paho.mqtt.client as mqtt

_logger = logging.getLogger(__name__)


class Mqtt:
    def __init__(self, hostname, port=1883):
        self._mqtthost = hostname
        self._mqttport = port

        self.client = mqtt.Client()

    def connect(self):
        _logger.info(f"Connecting to MQTT host '{self._mqtthost}:{self._mqttport}'")

        self.client.connect(self._mqtthost, self._mqttport, 60)
        self.client.loop_start()

    def publish(self, topic, value):
        _logger.debug(f"Publishing MQTT message to topic '{topic}' with value '{value}'")
        self.client.publish(topic, value)
