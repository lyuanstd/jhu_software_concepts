import subprocess
from pathlib import Path
import psycopg
import sys
BASE_DIR = Path(__file__).resolve().parent.parent
MODULE_2_DIR = BASE_DIR / "module_2"
sys.path.append(str(MODULE_2_DIR))
import os

def refresh_database():
    from scrape import scrape_data

    from load_data import (
        CLEAN_DATA_PATH,
        create_table_if_not_exists,
        insert_data,
        load_json_data,
    )

    # Scrape only the newest 3 pages for faster refresh
    scrape_data(max_pages=3, use_progress=False)

    # run Module 2 clean.py to clean new data, but skip the LLM process
    subprocess.run(
        ["python", str(MODULE_2_DIR / "clean.py")],
        check=True
    )

    # load the cleaned non-LLM data and append new records to PostgreSQL
    records = load_json_data(CLEAN_DATA_PATH)

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        conn = psycopg.connect(database_url)
    else:
        conn = psycopg.connect(
            dbname="gradcafe",
            user="lyuan"
        )

    create_table_if_not_exists(conn)
    inserted_count = insert_data(conn, records)

    conn.close()

    return inserted_count

if __name__ == "__main__":  # pragma: no cover
    count = refresh_database()
    print(f"{count} new records inserted.")