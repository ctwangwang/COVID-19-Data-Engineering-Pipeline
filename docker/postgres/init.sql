-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables
CREATE TABLE IF NOT EXISTS covid_daily_stats (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    confirmed INTEGER,
    deaths INTEGER,
    recovered INTEGER,
    active INTEGER,
    critical INTEGER,
    mortality_rate FLOAT,
    recovery_rate FLOAT,
    active_rate FLOAT,
    extraction_date TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_country ON covid_daily_stats(country);
CREATE INDEX idx_extraction_date ON covid_daily_stats(extraction_date);

-- Create update trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_covid_daily_stats_updated_at
    BEFORE UPDATE ON covid_daily_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
