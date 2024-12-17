# src/extractors/covid_extractor.py

import requests
import pandas as pd
from datetime import datetime
import logging
import json
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class COVIDDataExtractor:
    """Class to handle extraction of COVID-19 data from various sources"""

    def __init__(self, api_url=None):
        """Initialize the extractor with API URLs"""
        self.api_urls = {
            "countries": "https://disease.sh/v3/covid-19/countries",
            "global": "https://disease.sh/v3/covid-19/all",
            "historical": "https://disease.sh/v3/covid-19/historical",
        }
        # Override default URL if provided
        if api_url:
            self.api_urls["countries"] = api_url

        # Create data directory if it doesn't exist
        self.data_dir = "raw_data"
        os.makedirs(self.data_dir, exist_ok=True)

    def fetch_data(self, data_type="countries"):
        """Fetch COVID-19 data from specified API endpoint"""
        try:
            url = self.api_urls.get(data_type)
            if not url:
                raise ValueError(f"Invalid data type: {data_type}")

            logger.info(f"Fetching {data_type} data from {url}")
            response = requests.get(url)
            response.raise_for_status()

            # Save raw data
            self._save_raw_data(response.json(), data_type)

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Error fetching data: {str(e)}")
            raise

    def _save_raw_data(self, data, data_type):
        """Save raw data to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.data_dir}/covid_{data_type}_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(data, f)
        logger.info(f"Raw data saved to {filename}")

    def transform_data(self, raw_data):
        """Transform raw JSON data into a pandas DataFrame"""
        try:
            logger.info("Transforming raw data into DataFrame")

            # Convert to DataFrame
            if isinstance(raw_data, list):
                df = pd.DataFrame(raw_data)
            else:
                df = pd.DataFrame([raw_data])

            # Add metadata
            df["extraction_date"] = datetime.now()
            df["data_source"] = "disease.sh API"

            # Select and rename relevant columns
            if "countryInfo" in df.columns:
                # Expand countryInfo dictionary into separate columns
                country_info = pd.json_normalize(df["countryInfo"])
                df = pd.concat([df.drop("countryInfo", axis=1), country_info], axis=1)

            # Rename columns for consistency
            columns_mapping = {
                "country": "country",
                "cases": "confirmed",
                "deaths": "deaths",
                "recovered": "recovered",
                "active": "active",
                "critical": "critical",
                "tests": "tests",
                "population": "population",
                "continent": "continent",
                "lat": "latitude",
                "long": "longitude",
                "extraction_date": "extraction_date",
                "data_source": "data_source",
            }

            # Select only columns that exist in the DataFrame
            existing_columns = [
                col for col in columns_mapping.keys() if col in df.columns
            ]
            df = df[existing_columns].rename(
                columns={col: columns_mapping[col] for col in existing_columns}
            )

            return df

        except Exception as e:
            logger.error(f"Error transforming data: {str(e)}")
            raise

    def extract_and_transform(self, data_type="countries"):
        """Combine extraction and transformation into a single method"""
        raw_data = self.fetch_data(data_type)
        return self.transform_data(raw_data)

    def save_transformed_data(self, df, output_format="csv"):
        """Save transformed data to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.data_dir}/covid_transformed_{timestamp}.{output_format}"

        if output_format == "csv":
            df.to_csv(filename, index=False)
        elif output_format == "parquet":
            df.to_parquet(filename, index=False)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        logger.info(f"Transformed data saved to {filename}")
        return filename
