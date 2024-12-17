import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """Class to handle data validation"""

    def __init__(self):
        """Initialize the validator with required columns and data types"""
        self.required_columns = [
            "country",
            "confirmed",
            "deaths",
            "recovered",
            "active",
            "critical",
            "extraction_date",
        ]

        self.numeric_columns = [
            "confirmed",
            "deaths",
            "recovered",
            "active",
            "critical",
        ]

    def validate_schema(self, df):
        """Validate the DataFrame schema"""
        try:
            logger.info("Validating data schema")

            # Check for required columns
            missing_columns = set(self.required_columns) - set(df.columns)
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            return True

        except Exception as e:
            logger.error(f"Schema validation error: {str(e)}")
            raise

    def validate_data_quality(self, df):
        """Validate data quality"""
        try:
            logger.info("Validating data quality")

            # Check for null values in required fields
            null_counts = df[self.required_columns].isnull().sum()
            if null_counts.any():
                logger.warning(
                    f"Null values found in columns: \n{null_counts[null_counts > 0]}"
                )

            # Validate numeric columns are non-negative
            for col in self.numeric_columns:
                if (df[col] < 0).any():
                    raise ValueError(f"Negative values found in column: {col}")

            # Validate confirmed cases >= deaths + recovered
            invalid_totals = df[df["confirmed"] < (df["deaths"] + df["recovered"])]
            if not invalid_totals.empty:
                logger.warning(
                    f"Found {len(invalid_totals)} rows where confirmed < deaths + recovered"
                )

            return True

        except Exception as e:
            logger.error(f"Data quality validation error: {str(e)}")
            raise

    def validate_data(self, df):
        """Run all validations"""
        try:
            self.validate_schema(df)
            self.validate_data_quality(df)
            logger.info("All validations passed successfully")
            return True
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            raise
