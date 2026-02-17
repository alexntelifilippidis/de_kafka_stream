import os

from dotenv import load_dotenv

from app.kafka.kafka_client import KafkaConsumerClient
from app.utils.logger import get_logger

# Load environment variables from .env file
load_dotenv()

# Configure logger
logger = get_logger(name=__name__, level=os.getenv("LOG_LEVEL", "INFO"))


def process_employee_message(message) -> None:
    """Process and display employee message data."""
    employee_data = message.value

    logger.info(f"📨 Processing message from topic '{message.topic}'")
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

        # Convert max_messages to int if provided
        max_messages_int = int(max_messages) if max_messages else None

        logger.debug(f"📊 Configured to consume from topic '{topic}'")
        logger.debug(f"   └─ Consumer Group: {consumer_group_id}")
        logger.debug(f"   └─ Auto Offset Reset: {auto_offset_reset}")
        logger.debug(f"   └─ Max Messages: {max_messages_int or 'unlimited'}")

        # Initialize Kafka consumer client
        kafka_consumer = KafkaConsumerClient(
            group_id=consumer_group_id, auto_offset_reset=auto_offset_reset
        )

        # Subscribe to topic
        kafka_consumer.subscribe(topic)

        logger.info("👂 Listening for messages... (Press Ctrl+C to stop)")
        logger.info("=" * 80)

        # Consume messages
        message_count = 0
        for message in kafka_consumer.consume_messages(max_messages=max_messages_int):
            message_count += 1
            logger.info(f"\n{'=' * 80}")
            logger.info(f"Message #{message_count}")
            logger.info(f"{'=' * 80}")

            process_employee_message(message)

            logger.info(f"{'=' * 80}\n")

        logger.info(f"✅ Consumer completed successfully - processed {message_count} message(s)")

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


