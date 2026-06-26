-- Staging tables for WC2026 pipeline
-- Each table holds raw JSON blobs from one API endpoint, one row per snapshot load.
-- Columns are identical across all five; dbt reshapes these into clean tables later.

CREATE TABLE IF NOT EXISTS stg_matches(
    id SERIAL PRIMARY KEY,
    snap_shot_date TEXT NOT NULL,
    loaded_at TIMESTAMPTZ DEFAULT now(),
    raw JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS stg_standings(
    id SERIAL PRIMARY KEY,
    snap_shot_date TEXT NOT NULL,
    loaded_at TIMESTAMPTZ DEFAULT now(),
    raw JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS stg_scorers(
    id SERIAL PRIMARY KEY,
    snap_shot_date TEXT NOT NULL,
    loaded_at TIMESTAMPTZ DEFAULT now(),
    raw JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS stg_teams(
    id SERIAL PRIMARY KEY,
    snap_shot_date TEXT NOT NULL,
    loaded_at TIMESTAMPTZ DEFAULT now(),
    raw JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS stg_metadata(
    id SERIAL PRIMARY KEY,
    snap_shot_date TEXT NOT NULL,
    loaded_at TIMESTAMPTZ DEFAULT now(),
    raw JSONB NOT NULL
);