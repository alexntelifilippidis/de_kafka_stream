import os
import time

from dotenv import load_dotenv
from risingwave import RisingWave, RisingWaveConnOptions

from app.utils.logger import get_logger

# Load environment variables from .env file
load_dotenv()

# Configure logger
logger = get_logger(name=__name__, level=os.getenv("LOG_LEVEL", "INFO"))


def get_risingwave_client():
    """Get a RisingWave client instance with connection options."""
    return RisingWave(
        RisingWaveConnOptions.from_connection_info(
            host=os.getenv("RISINGWAVE_HOST", "localhost"),
            port=int(os.getenv("RISINGWAVE_PORT", 4566)),
            user=os.getenv("RISINGWAVE_USER", "root"),
            password=os.getenv("RISINGWAVE_PASSWORD", ""),
            database="dev"
        )
    )


def create_kafka_streaming_table():
    """Create a streaming table in RisingWave that reads from Kafka."""

    kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
    kafka_topic = os.getenv("KAFKA_TOPIC", "codehub")

    # For Kafka connector, we need to use the internal network address (kafka:9092)
    # when RisingWave is running in Docker
    internal_kafka_servers = "kafka:9092"

    # SQL to create the streaming table
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS employees (
        employee_id VARCHAR,
        name VARCHAR,
        seniority VARCHAR,
        domain VARCHAR,
        years_of_experience INTEGER,
        specialization VARCHAR,
        timestamp TIMESTAMPTZ,
        PRIMARY KEY (employee_id)
    ) WITH (
        connector = 'kafka',
        topic = '{kafka_topic}',
        properties.bootstrap.server = '{internal_kafka_servers}',
        scan.startup.mode = 'earliest'
    ) FORMAT PLAIN ENCODE JSON;
    """

    try:
        rw = get_risingwave_client()
        with rw.getconn() as conn:
            logger.info(f"Creating streaming table 'employees' from Kafka topic '{kafka_topic}'")
            logger.debug(f"Using Kafka bootstrap servers: {internal_kafka_servers}")
            conn.execute(create_table_sql)
            logger.info("✅ Streaming table 'employees' created successfully")
            logger.info("Note: Give RisingWave a moment to start consuming from Kafka")

    except Exception as e:
        logger.error(f"❌ Failed to create streaming table: {e}", exc_info=True)
        raise


def query_streaming_table(limit=10):
    """Query the streaming table to see the data."""
    try:
        rw = get_risingwave_client()
        with rw.getconn() as conn:
            query = f"SELECT * FROM employees ORDER BY timestamp DESC LIMIT {limit};"
            logger.info(f"Querying employees table (limit: {limit})")
            result = conn.execute(query)

            results = result.fetchall()

            if results:
                logger.info(f"Found {len(results)} records:")
                for row in results:
                    logger.info(f"  {row}")
            else:
                logger.info("No records found in employees table")

            return results

    except Exception as e:
        logger.error(f"❌ Failed to query streaming table: {e}", exc_info=True)
        raise


def drop_streaming_table():
    """Drop the streaming table (useful for cleanup/reset)."""
    try:
        rw = get_risingwave_client()
        with rw.getconn() as conn:
            logger.info("Dropping streaming table 'employees'")
            conn.execute("DROP TABLE IF EXISTS employees;")
            logger.info("✅ Streaming table 'employees' dropped successfully")

    except Exception as e:
        logger.error(f"❌ Failed to drop streaming table: {e}", exc_info=True)
        raise


def main():
    """Main function to demonstrate RisingWave streaming table operations."""
    logger.info("🚀 Starting RisingWave streaming table setup...")

    try:
        # Create the streaming table
        create_kafka_streaming_table()

        logger.info("⏳ Waiting 5 seconds for RisingWave to stabilize and start consuming...")
        time.sleep(5)

        # Query the table to verify it's working
        logger.info("📊 Querying the streaming table...")
        query_streaming_table(limit=10)

        logger.info("✅ RisingWave streaming table setup completed successfully")

    except Exception as e:
        logger.error(f"❌ Failed to setup RisingWave streaming table: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()


