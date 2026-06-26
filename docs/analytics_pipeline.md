# World Cup 2026 Analytics Pipeline

## Problem statement

An end-to-end ELT pipeline that captures a daily snapshot of 2026 World Cup data and serves it to an interactive dashboard. The data source only exposes *current* state with no history, so daily snapshots are what make the over-time story recoverable at all.

## Tech stack

| Layer | Tool |
|---|---|
| Data source | football-data.org API |
| Extraction | Python |
| Data lake | AWS S3 |
| Warehouse | PostgreSQL (AWS RDS) |
| Transformation | dbt |
| Compute / scheduling | AWS EC2 + cron |
| Dashboard | Streamlit (Plotly) |
| Local dev | Docker |

## Architecture

API → Python extract → S3 (raw JSON) → Postgres staging → dbt (star schema) → Streamlit dashboard.

Runs daily on EC2 via cron: extract current state, archive raw JSON to S3, load into Postgres staging, rebuild analytical tables with dbt. Warehouse on RDS; dashboard reads from it directly.
