from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    MetaData,
)
from datetime import datetime
import logging
from sqlalchemy import text
import pandas as pd

logger = logging.getLogger(__name__)


class DataWarehouse:
    """Class to handle data warehouse operations"""

    def __init__(self, connection_string):
        """Initialize the data warehouse connection and create table if not exists"""
        self.connection_string = connection_string
        self.engine = create_engine(connection_string)
        self.metadata = MetaData()

        # Define the table structure
        self.covid_daily_stats = Table(
            "covid_daily_stats",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("country", String(100)),
            Column("confirmed", Integer),
            Column("deaths", Integer),
            Column("recovered", Integer),
            Column("active", Integer),
            Column("critical", Integer),
            Column("mortality_rate", Float),
            Column("recovery_rate", Float),
            Column("active_rate", Float),
            Column("extraction_date", DateTime),
            Column("last_updated", DateTime, default=datetime.now),
            extend_existing=True,
        )

        # Create tables if they don't exist
        try:
            self.metadata.create_all(self.engine)
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database tables: {str(e)}")
            raise

    def init_database(self):
        """Initialize the database schema"""
        try:
            logger.info("Initializing database schema")
            self.metadata.create_all(self.engine)
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    def save_to_warehouse(self, df, table_name="covid_daily_stats", if_exists="append"):
        try:
            logger.info(f"Saving data to warehouse table: {table_name}")

            # Convert extraction_date to datetime if it's a string
            if df["extraction_date"].dtype == "object":
                df["extraction_date"] = pd.to_datetime(df["extraction_date"])

            # Get the current date
            current_date = df["extraction_date"].iloc[0].strftime("%Y-%m-%d")

            # Create database transaction
            with self.engine.begin() as connection:
                # Delete existing records for the same date
                delete_query = text(f"""
                    DELETE FROM {table_name}
                    WHERE DATE(extraction_date) = :current_date
                """)
                connection.execute(delete_query, {"current_date": current_date})

                # Add last_updated timestamp
                df["last_updated"] = datetime.now()

                # Save to database
                df.to_sql(
                    name=table_name, con=connection, if_exists="append", index=False
                )

            logger.info(f"Successfully saved {len(df)} records to {table_name}")

        except Exception as e:
            logger.error(f"Error saving to warehouse: {str(e)}")
            raise

    def get_latest_stats(self):
        """Retrieve the latest COVID statistics from the warehouse"""
        try:
            query = """
                SELECT DISTINCT ON (country)
                    country, confirmed, deaths, recovered, active, critical,
                    mortality_rate, recovery_rate, active_rate, extraction_date
                FROM covid_daily_stats
                ORDER BY country, extraction_date DESC
            """
            return pd.read_sql(query, self.engine)
        except Exception as e:
            logger.error(f"Error retrieving latest stats: {str(e)}")
            raise
