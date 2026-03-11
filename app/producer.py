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


def resolve_partition(partition_env: str, num_partitions: int, message_index: int) -> int | None:
    """
    Resolve which Kafka partition to use for a message.

    Rules:
      - PARTITION=-1  → random partition chosen per message across num_partitions
      - PARTITION=N   → always use partition N (fixed); validated against num_partitions
      - PARTITION not set (defaults to -1) → random
    """
    value = int(partition_env)
    if value < 0:
        # Random partition across the topic's partitions
        return random.randint(0, num_partitions - 1)
    if value >= num_partitions:
        raise ValueError(
            f"Requested partition {value} does not exist. "
            f"Topic only has {num_partitions} partition(s) (0–{num_partitions - 1})."
        )
    return value


def get_topic_partition_count(bootstrap_servers: list[str], topic: str) -> int:
    """Fetch the real partition count for a topic directly from the Kafka broker."""
    from kafka import KafkaAdminClient
    from kafka.admin import NewTopic  # noqa: F401 – just ensuring import is ok

    try:
        admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        metadata = admin.describe_topics([topic])
        admin.close()
        if metadata and metadata[0].get("partitions"):
            count = len(metadata[0]["partitions"])
            logger.debug(f"Broker reports {count} partition(s) for topic '{topic}'")
            return count
    except Exception as e:
        logger.warning(f"Could not fetch partition count from broker: {e}. Falling back to NUM_PARTITIONS env var.")
    return None


def main():
    logger.info("🚀 Starting Kafka Stream application...")
    kafka_client = None

    try:
        # Initialize Kafka client
        kafka_client = KafkaClient()

        # Get configuration from environment
        topic = os.getenv("KAFKA_TOPIC", "employees")
        num_messages = int(os.getenv("NUM_MESSAGES", "1"))
        # PARTITION=-1 (default) → random per message; PARTITION=N → fixed partition N
        partition_env = os.getenv("PARTITION", "-1")
        # Try to get the real partition count from the broker; fall back to env var
        broker_partition_count = get_topic_partition_count(kafka_client.bootstrap_servers, topic)
        num_partitions = broker_partition_count if broker_partition_count else int(os.getenv("NUM_PARTITIONS", "3"))
        logger.info(f"📡 Topic '{topic}' has {num_partitions} partition(s)")

        fixed_partition = int(partition_env)
        if fixed_partition < 0:
            logger.info(
                f"📊 Configured to send {num_messages} message(s) to topic '{topic}' "
                f"across {num_partitions} partition(s) (random per message)"
            )
        else:
            logger.info(
                f"📊 Configured to send {num_messages} message(s) to topic '{topic}' "
                f"on fixed partition {fixed_partition}"
            )

        # Send multiple messages
        for i in range(1, num_messages + 1):
            test_message = generate_random_employee_message(i)

            partition = resolve_partition(partition_env, num_partitions, i)

            logger.info(f"📤 Sending message {i}/{num_messages} to topic '{topic}' → partition {partition}")
            logger.debug(f"Message content: {test_message}")

            record_metadata = kafka_client.send_message(
                topic=topic, message=test_message, key=test_message["employee_id"], partition=partition
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
