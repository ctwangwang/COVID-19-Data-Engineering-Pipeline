import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import logging
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import our pipeline components
from src.config.config import DATABASE_URL
from src.extractors.covid_extractor import COVIDDataExtractor
from src.processors.covid_processor import COVIDDataProcessor
from src.storage.data_warehouse import DataWarehouse
from src.validators.data_validator import DataValidator

# Define default arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email": ["ctw2012105@@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


# Add a failure callback
def task_failure_callback(context):
    """
    Callback when task fails - can be used for Slack/Teams notifications
    """
    task_instance = context["task_instance"]
    task_name = task_instance.task_id
    dag_id = task_instance.dag_id
    error_message = context.get("exception")
    execution_date = context["execution_date"]

    error_msg = f"""
    DAG: {dag_id}
    Task: {task_name}
    Execution Date: {execution_date}
    Error: {error_message}
    """
    logging.error(error_msg)


# Define the tasks
def extract_data(**context):
    """Extract COVID-19 data from the API"""
    try:
        extractor = COVIDDataExtractor()
        df = extractor.extract_and_transform()

        # Convert DataFrame to dictionary with timestamp handling
        df_dict = df.copy()
        # Convert timestamp columns to string format
        for col in df_dict.select_dtypes(include=["datetime64[ns]"]).columns:
            df_dict[col] = df_dict[col].astype(str)

        # Push to XCom
        context["task_instance"].xcom_push(key="raw_data", value=df_dict.to_dict())
        return "Data extraction completed"
    except Exception as e:
        logging.error(f"Error in extract_data: {str(e)}")
        raise


def process_data(**context):
    """Process and transform the extracted data"""
    try:
        raw_data = context["task_instance"].xcom_pull(
            key="raw_data", task_ids="extract_data"
        )
        df = pd.DataFrame(raw_data)

        # Convert string back to datetime for timestamp columns
        if 'extraction_date' in df.columns:
            df['extraction_date'] = pd.to_datetime(df['extraction_date'])

        processor = COVIDDataProcessor()
        df = processor.clean_data(df)
        df = processor.calculate_metrics(df)
        df = processor.aggregate_data(df)

        # Convert timestamps to strings again before pushing to XCom
        df_dict = df.copy()
        for col in df_dict.select_dtypes(include=["datetime64[ns]"]).columns:
            df_dict[col] = df_dict[col].astype(str)

        context["task_instance"].xcom_push(
            key="processed_data", value=df_dict.to_dict()
        )
        return "Data processing completed"
    except Exception as e:
        logging.error(f"Error in process_data: {str(e)}")
        raise


def validate_data(**context):
    """Validate the processed data"""
    try:
        processed_data = context["task_instance"].xcom_pull(
            key="processed_data", task_ids="process_data"
        )
        df = pd.DataFrame(processed_data)

        # Data quality checks
        quality_checks = {
            "row_count": len(df) > 0,
            "no_nulls": df[["country", "confirmed", "deaths"]].isnull().sum().sum()
            == 0,
            "positive_values": (df[["confirmed", "deaths", "recovered"]] >= 0)
            .all()
            .all(),
        }

        failed_checks = [
            check for check, passed in quality_checks.items() if not passed
        ]

        if failed_checks:
            raise ValueError(f"Data quality checks failed: {failed_checks}")

        validator = DataValidator()
        validator.validate_data(df)
        return "Data validation completed"

    except Exception as e:
        logging.error(f"Error in validate_data: {str(e)}")
        raise


def store_data(**context):
    processed_data = context["task_instance"].xcom_pull(
        key="processed_data", task_ids="process_data"
    )
    df = pd.DataFrame(processed_data)

    warehouse = DataWarehouse(DATABASE_URL)
    warehouse.save_to_warehouse(df)
    return "Data stored successfully"


# Create the DAG
with DAG(
    "covid_data_pipeline",
    default_args=default_args,
    description="A DAG for COVID-19 data pipeline",
    schedule_interval="@daily",
    catchup=False,
) as dag:
    # Define the tasks
    extract_task = PythonOperator(
        task_id="extract_data",
        python_callable=extract_data,
        on_failure_callback=task_failure_callback,
        sla=timedelta(minutes=5),  # Task specific SLA
    )

    process_task = PythonOperator(task_id="process_data", python_callable=process_data)

    validate_task = PythonOperator(
        task_id="validate_data", python_callable=validate_data
    )

    store_task = PythonOperator(task_id="store_data", python_callable=store_data)

    # Set task dependencies
    extract_task >> process_task >> validate_task >> store_task
