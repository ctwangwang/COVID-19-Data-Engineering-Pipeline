import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class COVIDDataProcessor:
    """Class to handle processing and transformation of COVID-19 data"""

    def clean_data(self, df):
        """Clean the input DataFrame"""
        try:
            logger.info("Cleaning data")

            # Create a copy to avoid modifying the original DataFrame
            cleaned_df = df.copy()

            # Handle missing values
            numeric_columns = ["confirmed", "deaths", "recovered", "active", "critical"]
            cleaned_df[numeric_columns] = cleaned_df[numeric_columns].fillna(0)

            # Convert numeric columns to appropriate types
            cleaned_df[numeric_columns] = cleaned_df[numeric_columns].astype(int)

            # Clean country names (remove special characters, standardize spacing)
            cleaned_df["country"] = cleaned_df["country"].str.strip()

            return cleaned_df

        except Exception as e:
            logger.error(f"Error cleaning data: {str(e)}")
            raise

    def calculate_metrics(self, df):
        """Calculate additional metrics from the data"""
        try:
            logger.info("Calculating additional metrics")

            df = df.copy()

            # Calculate mortality rate
            df["mortality_rate"] = (df["deaths"] / df["confirmed"] * 100).round(2)

            # Calculate recovery rate
            df["recovery_rate"] = (df["recovered"] / df["confirmed"] * 100).round(2)

            # Calculate active case rate
            df["active_rate"] = (df["active"] / df["confirmed"] * 100).round(2)

            return df

        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            raise

    def aggregate_data(self, df):
        """Aggregate data by country"""
        try:
            logger.info("Aggregating data")
            # Keep track of the extraction_date before aggregation
            extraction_date = df["extraction_date"].iloc[
                0
            ]  # Take the first date since it should be the same for all rows
            aggregated = (
                df.groupby("country")
                .agg(
                    {
                        "confirmed": "sum",
                        "deaths": "sum",
                        "recovered": "sum",
                        "active": "sum",
                        "critical": "sum",
                        "mortality_rate": "mean",
                        "recovery_rate": "mean",
                        "active_rate": "mean",
                    }
                )
                .reset_index()
            )
            aggregated["extraction_date"] = extraction_date
            return aggregated

        except Exception as e:
            logger.error(f"Error aggregating data: {str(e)}")
            raise
