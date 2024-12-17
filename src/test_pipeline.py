import os
import sys
import logging
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.config.config import DATABASE_URL
from src.extractors.covid_extractor import COVIDDataExtractor
from src.processors.covid_processor import COVIDDataProcessor
from src.storage.data_warehouse import DataWarehouse
from src.validators.data_validator import DataValidator


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_pipeline():
    try:
        # 1. Extract Data
        logger.info("Starting data extraction...")
        extractor = COVIDDataExtractor()
        raw_df = extractor.extract_and_transform()
        logger.info(f"Extracted {len(raw_df)} records")

        # 2. Process Data
        logger.info("Processing data...")
        processor = COVIDDataProcessor()
        processed_df = processor.clean_data(raw_df)
        processed_df = processor.calculate_metrics(processed_df)
        processed_df = processor.aggregate_data(processed_df)
        logger.info("Data processing completed")

        # 3. Validate Data
        logger.info("Validating data...")
        validator = DataValidator()
        validator.validate_data(processed_df)
        logger.info("Data validation passed")

        # 4. Save to Warehouse
        
        logger.info("Saving to warehouse...")
        warehouse = DataWarehouse(DATABASE_URL)
        warehouse.save_to_warehouse(processed_df)
        logger.info("Pipeline completed successfully")

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise


if __name__ == "__main__":
    run_pipeline()
