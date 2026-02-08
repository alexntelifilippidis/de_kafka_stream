import os

from kafka import KafkaProducer
import json
from app.utils.logger import get_logger


class KafkaClient:
    def __init__(self):
        self.logger = get_logger(name=__name__, level=os.getenv("LOG_LEVEL", "INFO"))

        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
        self.client_id = os.getenv("KAFKA_CLIENT_ID", "kafka-client")

        self.logger.info("Initializing Kafka producer")
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            client_id=self.client_id,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        self.logger.info(f"Kafka producer initialized with bootstrap servers: {self.bootstrap_servers}, client_id: {self.client_id}")

    def send_message(self, topic, message, key=None):
        """Send a message to the specified Kafka topic."""
        self.logger.debug(f"Sending message to topic '{topic}' with key '{key}'")
        future = self.producer.send(topic, value=message, key=key)

        try:
            record_metadata = future.get(timeout=10)
            self.logger.info(
                f"Message sent successfully to topic '{topic}' "
                f"[partition: {record_metadata.partition}, offset: {record_metadata.offset}]"
            )
            return record_metadata
        except Exception as e:
            self.logger.error(f"Failed to send message to topic '{topic}': {e}")
            raise

    def close(self):
        """Close the producer connection."""
        self.logger.info("Closing Kafka producer")
        self.producer.close()
        self.logger.info("Kafka producer closed successfully")
