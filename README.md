


# COVID-19 Data Engineering Pipeline

## Project Overview
This project implements an end-to-end data engineering pipeline that extracts COVID-19 data from the disease.sh API, processes it, stores it in PostgreSQL, and visualizes it using Streamlit. The entire pipeline is orchestrated using Apache Airflow and containerized with Docker.

![Project Architecture](./images/architecture.png)

## Technologies Used
- Python 3.9+
- Apache Airflow
- PostgreSQL
- Docker & Docker Compose
- Streamlit
- Pandas, SQLAlchemy, and other Python libraries

## Project Structure
```
COVID-19-Data-Engineering-Pipeline/
├── dags/
│   └── covid_pipeline_dag.py
├── docker/
│   ├── postgres/
│   │   └── init.sql
│   └── airflow/
│       └── Dockerfile
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── extractors/
│   │   ├── __init__.py
│   │   └── covid_extractor.py
│   ├── processors/
│   │   ├── __init__.py
│   │   └── covid_processor.py
│   ├── storage/
│   │   ├── __init__.py
│   │   └── data_warehouse.py
│   ├── validators/
│   │   ├── __init__.py
│   │   └── data_validator.py
│   └── dashboard/
│       └── covid_dashboard.py
├── .env.example
├── docker-compose.yml
└── requirements.txt
```

## Prerequisites
- Python 3.9+
- Docker Desktop
- Git

## Installation & Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/COVID-19-Data-Engineering-Pipeline.git
cd COVID-19-Data-Engineering-Pipeline
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configurations
```

5. Start Docker containers:
```bash
docker-compose up -d
```

## Running the Pipeline

1. Access Airflow UI:
   - Navigate to `http://localhost:8080`
   - Login with default credentials (username: admin, password: admin)
   - Enable the COVID data pipeline DAG

2. View the Dashboard:
```bash
streamlit run src/dashboard/covid_dashboard.py
```
Navigate to `http://localhost:8501` in your browser.

## Pipeline Components

1. **Data Extraction**
   - Sources data from disease.sh API
   - Extracts country-wise COVID-19 statistics

2. **Data Processing**
   - Cleans and transforms raw data
   - Calculates additional metrics
   - Validates data quality

3. **Data Storage**
   - Stores processed data in PostgreSQL
   - Maintains historical records

4. **Data Visualization**
   - Interactive Streamlit dashboard
   - Key metrics and trends visualization

## Configuration

Key configurations are managed through environment variables:
```
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_DB=covid_db
POSTGRES_HOST=postgres
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Contact
Chester Wang - ctw2012105@gmail.com
Project Link: [https://github.com/yourusername/COVID-19-Data-Engineering-Pipeline](https://github.com/yourusername/COVID-19-Data-Engineering-Pipeline)
```

