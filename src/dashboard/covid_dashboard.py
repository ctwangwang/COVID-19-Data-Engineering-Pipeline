import os
import sys
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go

# Add the project root directory to Python path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(project_root)

# Now import from src
from src.config.config import DATABASE_URL


def load_data():
    """Load data from PostgreSQL database"""
    # Create connection string directly (not using DATABASE_URL from config)
    connection_string = "postgresql://admin:admin@localhost:5432/covid_db"
    engine = create_engine(connection_string)

    query = """
        SELECT * FROM covid_daily_stats
        WHERE extraction_date = (SELECT MAX(extraction_date) FROM covid_daily_stats)
    """
    return pd.read_sql(query, engine)


def main():
    st.title("COVID-19 Dashboard")

    # Load data
    df = load_data()

    # Global statistics
    st.header("Global Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Cases", f"{df['confirmed'].sum():,.0f}")
    with col2:
        st.metric("Total Deaths", f"{df['deaths'].sum():,.0f}")
    with col3:
        st.metric("Average Mortality Rate", f"{df['mortality_rate'].mean():.2f}%")

    # Top 10 countries by confirmed cases
    st.header("Top 10 Countries by Confirmed Cases")
    top_countries = df.nlargest(10, "confirmed")
    fig = px.bar(
        top_countries,
        x="country",
        y="confirmed",
        title="Top 10 Countries by Confirmed Cases",
    )
    st.plotly_chart(fig)

    # Mortality rate analysis
    st.header("Mortality Rate Analysis")
    mortality_fig = px.scatter(
        df,
        x="confirmed",
        y="mortality_rate",
        hover_data=["country"],
        title="Mortality Rate vs Confirmed Cases",
    )
    st.plotly_chart(mortality_fig)

    # Recovery analysis
    st.header("Recovery Analysis")
    top_recovery = df.nlargest(10, "recovery_rate")
    recovery_fig = px.bar(
        top_recovery,
        x="country",
        y="recovery_rate",
        title="Top 10 Countries by Recovery Rate",
    )
    st.plotly_chart(recovery_fig)


if __name__ == "__main__":
    main()
