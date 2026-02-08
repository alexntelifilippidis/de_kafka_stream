import os

from dotenv import load_dotenv

from app.kafka.kafka_client import KafkaClient
from app.utils.logger import get_logger

# Load environment variables from .env file
load_dotenv()

# Configure logger
logger = get_logger(name=__name__, level=os.getenv("LOG_LEVEL", "INFO"))


def main():
    logger.info("🚀 Starting Kafka Stream application...")
    kafka_client = None

    try:
        # Initialize Kafka client
        kafka_client = KafkaClient()

        # Get topic from environment
        topic = os.getenv("KAFKA_TOPIC", "employees")

        # Send test message about employee seniority and domain
        test_message = {
            "employee_id": "EMP-2024-001",
            "name": "John Doe",
            "seniority": "Senior",
            "domain": "Software Engineering",
            "years_of_experience": 8,
            "specialization": "Backend Development",
            "timestamp": "2024-01-15T10:30:00Z"
        }

        logger.info(f"📤 Sending test message to topic '{topic}'")
        record_metadata = kafka_client.send_message(
            topic=topic,
            message=test_message,
            key="EMP-2024-001"
        )
        logger.info(f"✅ Test message sent successfully: partition={record_metadata.partition}, offset={record_metadata.offset}")

        logger.info("✅ Application initialized successfully")

    except Exception as e:
        logger.error(f"❌ Application failed: {e}", exc_info=True)
        raise
    finally:
        if kafka_client:
            kafka_client.close()
        logger.info("🛑 Shutting down application...")


if __name__ == "__main__":
    main()
