import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if running in Docker
IN_AIRFLOW = os.getenv("AIRFLOW_HOME", False)

DATABASE_CONFIG = {
    "host": "covid_postgres" if IN_AIRFLOW else "localhost",
    "database": os.getenv("POSTGRES_DB", "covid_db"),
    "user": os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "admin"),
    "port": 5432,
}

# Create connection string
DATABASE_URL = f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
