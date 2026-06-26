#!/bin/bash

#world cup pipeline: extract -> load -> transform

cd /home/ubuntu/worldcup-2026-pipeline
source venv/bin/activate

echo "=== Pipeline run: $(date) ==="

echo "Extracting..."
python extract/extract_football_data.py

echo "Loading..."
python load/load_to_postgres.py

echo "Transforming (dbt)..."
cd wc_dbt
dbt run

echo "=== Pipeline complete: $(date) ==="