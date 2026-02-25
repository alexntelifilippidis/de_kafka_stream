import os

from dotenv import load_dotenv
from risingwave import RisingWave, RisingWaveConnOptions

# Load environment variables from .env file
load_dotenv()

# Connect to RisingWave instance on localhost with named parameters
rw = RisingWave(
    RisingWaveConnOptions.from_connection_info(
        host=os.getenv("RISINGWAVE_HOST", "localhost"),
        port=os.getenv("RISINGWAVE_PORT", 4566),
        user=os.getenv("RISINGWAVE_USER", "root"),
        password=os.getenv("RISINGWAVE_PASSWORD", ""),
        database="dev"
    )
)

# You can create a new SQL connection and execute operations under the with statement.
# This is the recommended way for python sdk usage.
with rw.getconn() as conn:
    print(conn)


