import os
import random
import time
from datetime import datetime

from dotenv import load_dotenv

from app.kafka.kafka_client import KafkaClient
from app.utils.logger import get_logger

# Load environment variables from .env file
load_dotenv()

# Configure logger
logger = get_logger(name=__name__, level=os.getenv("LOG_LEVEL", "INFO"))


def generate_random_employee_message(employee_number: int) -> dict:
    """Generate a random employee message with varying attributes."""

    # Random data pools
    names = [
        "John Doe",
        "Jane Smith",
        "Alice Johnson",
        "Bob Williams",
        "Charlie Brown",
        "Diana Prince",
        "Eve Davis",
        "Frank Miller",
        "Grace Lee",
        "Henry Wilson",
        "Ivy Martinez",
        "Jack Anderson",
        "Karen Taylor",
        "Leo Thomas",
        "Mia Moore",
    ]

    seniorities = ["Junior", "Mid-Level", "Senior", "Staff", "Principal", "Lead"]

    domains = [
        "Software Engineering",
        "Data Engineering",
        "DevOps",
        "Machine Learning",
        "Frontend Development",
        "Backend Development",
        "Full Stack Development",
        "Cloud Architecture",
        "Security Engineering",
        "QA Engineering",
    ]

    specializations = [
        "Backend Development",
        "Frontend Development",
        "API Design",
        "Database Design",
        "Microservices",
        "Cloud Infrastructure",
        "CI/CD",
        "Data Pipelines",
        "Real-time Systems",
        "Distributed Systems",
        "Mobile Development",
    ]

    # Generate random employee data
    employee_id = f"EMP-{datetime.now().year}-{str(employee_number).zfill(3)}"
    name = random.choice(names)
    seniority = random.choice(seniorities)
    domain = random.choice(domains)
    years_of_experience = random.randint(1, 20)
    specialization = random.choice(specializations)

    return {
        "employee_id": employee_id,
        "name": name,
        "seniority": seniority,
        "domain": domain,
        "years_of_experience": years_of_experience,
        "specialization": specialization,
        "timestamp": datetime.now().isoformat(),
    }


def main():
    logger.info("🚀 Starting Kafka Stream application...")
    kafka_client = None

    try:
        # Initialize Kafka client
        kafka_client = KafkaClient()

        # Get configuration from environment
        topic = os.getenv("KAFKA_TOPIC", "employees")
        num_messages = int(os.getenv("NUM_MESSAGES", "1"))

        logger.info(f"📊 Configured to send {num_messages} message(s) to topic '{topic}'")

        # Send multiple messages
        for i in range(1, num_messages + 1):
            test_message = generate_random_employee_message(i)

            logger.info(f"📤 Sending message {i}/{num_messages} to topic '{topic}'")
            logger.debug(f"Message content: {test_message}")

            record_metadata = kafka_client.send_message(
                topic=topic, message=test_message, key=test_message["employee_id"]
            )

            logger.info(
                f"✅ Message {i}/{num_messages} sent successfully: "
                f"partition={record_metadata.partition}, offset={record_metadata.offset}"
            )

            # Small delay between messages to avoid overwhelming the broker
            if i < num_messages:
                time.sleep(0.5)

        logger.info(f"✅ Application completed successfully - sent {num_messages} message(s)")

    except Exception as e:
        logger.error(f"❌ Application failed: {e}", exc_info=True)
        raise
    finally:
        if kafka_client:
            kafka_client.close()
        logger.info("🛑 Shutting down application...")


if __name__ == "__main__":
    main()
