import os

from dotenv import load_dotenv

from app.kafka.kafka_client import KafkaConsumerClient
from app.utils.logger import get_logger

# Load environment variables from .env file
load_dotenv()

# Configure logger
logger = get_logger(name=__name__, level=os.getenv("LOG_LEVEL", "INFO"))


def process_employee_message(message, message_number: int | None = None) -> None:
    """Process and display employee message data."""
    employee_data = message.value
    prefix = f"#{message_number} " if message_number else ""

    logger.info(f"📨 {prefix}Processing message from topic '{message.topic}'")
    logger.info(
        f"   └─ Partition: {message.partition}, Offset: {message.offset}, Key: {message.key}"
    )
    logger.info(f"   └─ Employee ID: {employee_data.get('employee_id')}")
    logger.info(f"   └─ Name: {employee_data.get('name')}")
    logger.info(f"   └─ Seniority: {employee_data.get('seniority')}")
    logger.info(f"   └─ Domain: {employee_data.get('domain')}")
    logger.info(f"   └─ Years of Experience: {employee_data.get('years_of_experience')}")
    logger.info(f"   └─ Specialization: {employee_data.get('specialization')}")
    logger.info(f"   └─ Timestamp: {employee_data.get('timestamp')}")
    logger.debug(f"Full message data: {employee_data}")


def main():
    logger.info("🚀 Starting Kafka Consumer application...")
    kafka_consumer = None

    try:
        # Get configuration from environment
        topic = os.getenv("KAFKA_TOPIC", "employees")
        consumer_group_id = os.getenv("KAFKA_CONSUMER_GROUP_ID", "employee-consumer-group")
        auto_offset_reset = os.getenv("KAFKA_AUTO_OFFSET_RESET", "earliest")
        max_messages = os.getenv("MAX_MESSAGES")

        # Batch-mode configuration
        # BATCH_MODE=true  → use consumer.poll() and process messages in chunks
        # BATCH_SIZE        → max records per poll call          (default: 100)
        # BATCH_TIMEOUT_MS  → ms to wait per poll before retry  (default: 3000)
        # MAX_BATCHES       → stop after N non-empty batches     (default: unlimited)
        batch_mode = os.getenv("BATCH_MODE", "false").lower() in ("1", "true", "yes")
        batch_size = int(os.getenv("BATCH_SIZE", "100"))
        batch_timeout_ms = int(os.getenv("BATCH_TIMEOUT_MS", "3000"))
        max_batches = os.getenv("MAX_BATCHES")
        max_batches_int = int(max_batches) if max_batches else None

        # Convert max_messages to int if provided
        max_messages_int = int(max_messages) if max_messages else None

        logger.debug(f"📊 Configured to consume from topic '{topic}'")
        logger.debug(f"   └─ Consumer Group: {consumer_group_id}")
        logger.debug(f"   └─ Auto Offset Reset: {auto_offset_reset}")
        logger.debug(f"   └─ Mode: {'BATCH' if batch_mode else 'single-message'}")
        if batch_mode:
            logger.debug(f"   └─ Batch Size: {batch_size} records/poll")
            logger.debug(f"   └─ Batch Timeout: {batch_timeout_ms} ms")
            logger.debug(f"   └─ Max Batches: {max_batches_int or 'unlimited'}")
        else:
            logger.debug(f"   └─ Max Messages: {max_messages_int or 'unlimited'}")

        # Initialize Kafka consumer client
        kafka_consumer = KafkaConsumerClient(
            group_id=consumer_group_id, auto_offset_reset=auto_offset_reset
        )

        # Subscribe to topic
        kafka_consumer.subscribe(topic)

        logger.info("👂 Listening for messages... (Press Ctrl+C to stop)")
        logger.info("=" * 80)

        # ── BATCH MODE ─────────────────────────────────────────────────────────
        if batch_mode:
            logger.info(
                f"📦 BATCH MODE enabled  "
                f"(batch_size={batch_size}, timeout_ms={batch_timeout_ms}, "
                f"max_batches={max_batches_int or 'unlimited'})"
            )
            total_messages = 0
            for batch_num, batch in kafka_consumer.consume_messages_batch(
                max_records=batch_size,
                timeout_ms=batch_timeout_ms,
                max_batches=max_batches_int,
            ):
                logger.info(f"\n{'=' * 80}")
                logger.info(f"📦 BATCH #{batch_num}")
                logger.info(f"{'=' * 80}")

                batch_msg_count = 0
                # batch is {TopicPartition: [ConsumerRecord, ...]}
                for tp, messages in batch.items():
                    logger.info(
                        f"  📂 Partition {tp.partition} — {len(messages)} message(s):"
                    )
                    for msg in messages:
                        total_messages += 1
                        batch_msg_count += 1
                        process_employee_message(msg, message_number=total_messages)

                logger.info(
                    f"{'=' * 80}\n"
                    f"✅ Batch #{batch_num} done — {batch_msg_count} msg(s) processed  "
                    f"(total so far: {total_messages})\n"
                )

            logger.info(
                f"✅ Batch consumer completed — processed {total_messages} message(s) "
                f"in {batch_num if total_messages else 0} batch(es)"
            )

        # ── SINGLE-MESSAGE MODE ────────────────────────────────────────────────
        else:
            message_count = 0
            for message in kafka_consumer.consume_messages(max_messages=max_messages_int):
                message_count += 1
                logger.info(f"\n{'=' * 80}")
                logger.info(f"Message #{message_count}")
                logger.info(f"{'=' * 80}")

                process_employee_message(message, message_number=message_count)

                logger.info(f"{'=' * 80}\n")

            logger.info(
                f"✅ Consumer completed successfully — processed {message_count} message(s)"
            )

    except KeyboardInterrupt:
        logger.info("⚠️  Consumer interrupted by user")
    except Exception as e:
        logger.error(f"❌ Consumer failed: {e}", exc_info=True)
        raise
    finally:
        if kafka_consumer:
            kafka_consumer.close()
        logger.info("🛑 Shutting down consumer application...")


if __name__ == "__main__":
    main()


