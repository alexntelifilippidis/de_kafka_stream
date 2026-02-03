import os

from dotenv import load_dotenv

from app.utils.logger import get_logger

# Load environment variables from .env file
load_dotenv()

# Configure logger
logger = get_logger(name=__name__, level=os.getenv("LOG_LEVEL", "INFO"))


def main():
    logger.info("🚀 Starting Kafka Stream application...")

    try:
        # TODO: Add application logic here
        logger.info("✅  Application initialized successfully")

    except Exception as e:
        logger.error(f"❌ Application failed: {e}", exc_info=True)
        raise
    finally:
        logger.info("🛑 Shutting down application...")


if __name__ == "__main__":
    main()
