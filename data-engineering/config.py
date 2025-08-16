import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load environment variables from .env file
load_dotenv()

# Source databas (read-only)
SOURCE_DB_URL = os.getenv("SOURCE_DB_URL", "postgresql://user:pass@localhost/clutter_haven")

# Prototype source database for testing
PROTOTYPE_DB_URL = os.getenv('PROTOTYPE_DB_URL', 'postgresql://postgres:password@localhost:5432/clutter_haven_test')

# Warehouse database
WAREHOUSE_DB_URL = os.getenv('WAREHOUSE_DB_URL', 'postgresql://user:pass@localhost/clutter_warehouse')

# Create engines
source_engine = create_engine(SOURCE_DB_URL)
source_prototype_engine = create_engine(PROTOTYPE_DB_URL)
warehouse_engine = create_engine(WAREHOUSE_DB_URL)