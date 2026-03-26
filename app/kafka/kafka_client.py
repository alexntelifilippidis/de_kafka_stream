import json
import os

from app.utils.logger import get_logger
from kafka import KafkaConsumer, KafkaProducer


class KafkaClient:
    def __init__(self):
        self.logger = get_logger(name=__name__, level=os.getenv("LOG_LEVEL", "INFO"))

        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
        self.client_id = os.getenv("KAFKA_CLIENT_ID", "kafka-client")

        self.logger.info("Initializing Kafka producer")
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            client_id=self.client_id,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )
        self.logger.info(
            f"Kafka producer initialized with bootstrap servers: "
            f"{self.bootstrap_servers}, client_id: {self.client_id}"
        )

    def send_message(self, topic, message, key=None, partition=None):
        """Send a message to the specified Kafka topic."""
        self.logger.debug(f"Sending message to topic '{topic}' with key '{key}'")
        future = self.producer.send(topic, value=message, key=key, partition=partition)

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


class KafkaConsumerClient:
    def __init__(self, group_id=None, auto_offset_reset="earliest"):
        self.logger = get_logger(name=__name__, level=os.getenv("LOG_LEVEL", "INFO"))

        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
        self.client_id = os.getenv("KAFKA_CLIENT_ID", "kafka-consumer-client")
        self.group_id = group_id or os.getenv("KAFKA_CONSUMER_GROUP_ID", "kafka-consumer-group")
        self.auto_offset_reset = auto_offset_reset

        self.consumer = None
        self.logger.info(
            f"Kafka consumer client initialized with bootstrap servers: {self.bootstrap_servers}, "
            f"client_id: {self.client_id}, group_id: {self.group_id}"
        )

    def subscribe(self, topics):
        """Subscribe to one or more Kafka topics."""
        if isinstance(topics, str):
            topics = [topics]

        self.logger.info(f"Initializing Kafka consumer for topics: {topics}")
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            client_id=self.client_id,
            group_id=self.group_id,
            auto_offset_reset=self.auto_offset_reset,
            enable_auto_commit=True,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
        )
        self.logger.info(f"Kafka consumer subscribed to topics: {topics}")

    def consume_messages(self, max_messages=None, timeout_ms=1000):
        """
        Consume messages from subscribed topics.

        Args:
            max_messages: Maximum number of messages to consume (None for unlimited)
            timeout_ms: Timeout in milliseconds for polling

        Yields:
            Message objects with topic, partition, offset, key, and value
        """
        if self.consumer is None:
            raise RuntimeError("Consumer not initialized. Call subscribe() first.")

        self.logger.info(f"Starting to consume messages (max: {max_messages or 'unlimited'})")
        messages_consumed = 0

        try:
            for message in self.consumer:
                self.logger.debug(
                    f"Received message from topic '{message.topic}' "
                    f"[partition: {message.partition}, offset: {message.offset}]"
                )
                messages_consumed += 1
                yield message

                if max_messages and messages_consumed >= max_messages:
                    self.logger.info(f"Reached maximum messages limit: {max_messages}")
                    break

        except KeyboardInterrupt:
            self.logger.info("Consumer interrupted by user")
        finally:
            self.logger.info(f"Total messages consumed: {messages_consumed}")

    def consume_messages_batch(self, max_records=500, timeout_ms=3000, max_batches=None):
        """
        Consume messages in **batches** using consumer.poll().

        Each poll call returns up to `max_records` messages grouped by TopicPartition.
        This is far more efficient than single-message iteration when throughput matters.

        Args:
            max_records  : Max messages returned in a single poll call (default 500).
            timeout_ms   : How long to wait for messages before returning an empty batch (ms).
            max_batches  : Stop after this many non-empty poll rounds (None = unlimited).

        Yields:
            (batch_number: int, batch: dict[TopicPartition, list[ConsumerRecord]])
            — one yield per non-empty poll round.
        """
        if self.consumer is None:
            raise RuntimeError("Consumer not initialized. Call subscribe() first.")

        self.logger.info(
            f"🚀 Starting BATCH consumption  "
            f"(max_records/batch={max_records}, timeout_ms={timeout_ms}, "
            f"max_batches={max_batches or 'unlimited'})"
        )
        batch_count = 0
        total_messages = 0

        try:
            while True:
                # poll() → {TopicPartition: [ConsumerRecord, ...]}
                raw_batch = self.consumer.poll(timeout_ms=timeout_ms, max_records=max_records)

                if not raw_batch:
                    self.logger.debug("⏳ Empty poll — no messages yet, waiting…")
                    continue

                batch_count += 1
                batch_size = sum(len(msgs) for msgs in raw_batch.values())
                total_messages += batch_size

                self.logger.info(
                    f"📦 Batch #{batch_count}: {batch_size} message(s) "
                    f"across {len(raw_batch)} partition(s)"
                )
                for tp, msgs in raw_batch.items():
                    self.logger.debug(
                        f"   └─ {tp.topic}[{tp.partition}]: {len(msgs)} msg(s)  "
                        f"offsets {msgs[0].offset}–{msgs[-1].offset}"
                    )

                yield batch_count, raw_batch

                if max_batches and batch_count >= max_batches:
                    self.logger.info(f"Reached max_batches limit: {max_batches}")
                    break

        except KeyboardInterrupt:
            self.logger.info("Batch consumer interrupted by user")
        finally:
            self.logger.info(
                f"✅ Batch consumption finished — "
                f"batches={batch_count}, total_messages={total_messages}"
            )

    def close(self):
        """Close the consumer connection."""
        if self.consumer:
            self.logger.info("Closing Kafka consumer")
            self.consumer.close()
            self.logger.info("Kafka consumer closed successfully")

