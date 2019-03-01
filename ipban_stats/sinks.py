from .mqtt import Mqtt
import logging

_logger = logging.getLogger()


class MqttSink:
    def __init__(self, hostname, port, topic_root):
        _logger.info(f"Creating MQTT sink for host '{hostname}:{port}")
        self._topic_root = topic_root
        self._mqtt = Mqtt(hostname, port)
        self._mqtt.connect()

    def publish(self, module_name, reading_name, value):
        topic = f"{self._topic_root}/{module_name}/{reading_name}"
        self._mqtt.publish(topic, value)
