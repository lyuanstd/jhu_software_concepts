import psycopg
import json
from datetime import datetime
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
LLM_DATA_PATH = BASE_DIR / "module_2" / "llm_extend_applicant_data.json"
CLEAN_DATA_PATH = BASE_DIR / "module_2" / "applicant_data_for_llm.json"

def get_database_url():
    """Return the database URL from the environment, if available."""
    return os.getenv("DATABASE_URL")

# load GradCafe dataset from JSON
# use llm-processed data for requesting existing data
# use unprocessed data for updated analysis
def load_json_data(path=LLM_DATA_PATH):
    with open(path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)

# convert string dates into Python date objects
def parse_date(date_text):
    if not date_text:
        return None
    try:
        return datetime.strptime(date_text, "%b %d, %Y").date()
    except ValueError:
        return None

# convert GPA/GRE values to floats
def parse_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None

# create / reset table for initial request
def create_table(conn):
    cur = conn.cursor()
    cur.execute("""
        DROP TABLE IF EXISTS applicants;
        CREATE TABLE applicants (
            p_id SERIAL PRIMARY KEY,
            program TEXT,
            comments TEXT,
            date_added DATE,
            url TEXT UNIQUE,
            status TEXT,
            term TEXT,
            us_or_international TEXT,
            gpa FLOAT,
            gre FLOAT,
            gre_v FLOAT,
            gre_aw FLOAT,
            degree TEXT,
            llm_generated_program TEXT,
            llm_generated_university TEXT
        );
    """)

    conn.commit()
    cur.close()

# create table for newly available data
def create_table_if_not_exists(conn):
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS applicants (
            p_id SERIAL PRIMARY KEY,
            program TEXT,
            comments TEXT,
            date_added DATE,
            url TEXT UNIQUE,
            status TEXT,
            term TEXT,
            us_or_international TEXT,
            gpa FLOAT,
            gre FLOAT,
            gre_v FLOAT,
            gre_aw FLOAT,
            degree TEXT,
            llm_generated_program TEXT,
            llm_generated_university TEXT
        );
    """)

    conn.commit()
    cur.close()

# insert cleaned records
def insert_data(conn, records):
    cur = conn.cursor()

    # SQL template for one applicant record
    insert_sql = """
        INSERT INTO applicants (
            program,
            comments,
            date_added,
            url,
            status,
            term,
            us_or_international,
            gpa,
            gre,
            gre_v,
            gre_aw,
            degree,
            llm_generated_program,
            llm_generated_university
        )
        VALUES (
            %(program)s,
            %(comments)s,
            %(date_added)s,
            %(url)s,
            %(status)s,
            %(term)s,
            %(us_or_international)s,
            %(gpa)s,
            %(gre)s,
            %(gre_v)s,
            %(gre_aw)s,
            %(degree)s,
            %(llm_generated_program)s,
            %(llm_generated_university)s
        )
        ON CONFLICT (url) DO NOTHING;
    """

    cleaned_records = []

    # Convert JSON fields into database-ready fields
    for item in records:
        cleaned_records.append({
            "program": item.get("program"),
            "comments": item.get("comment"),
            "date_added": parse_date(item.get("date_added")),
            "url": item.get("entry_url"),
            "status": item.get("applicant_status"),
            "term": item.get("season"),
            "us_or_international": item.get("student_type"),
            "gpa": parse_float(item.get("gpa")),
            "gre": parse_float(item.get("gre_score")),
            "gre_v": parse_float(item.get("gre_v_score")),
            "gre_aw": parse_float(item.get("gre_aw")),
            "degree": item.get("degree"),
            "llm_generated_program": item.get("llm-generated-program") or item.get("program_name"),
            "llm_generated_university": item.get("llm-generated-university") or item.get("university"),
        })

    cur.executemany(insert_sql, cleaned_records)
    inserted_count = cur.rowcount

    conn.commit()
    cur.close()

    return inserted_count

def main():
    # connect to DATABASE_URL or local PostgreSQL database
    database_url = get_database_url()

    if database_url:
        conn = psycopg.connect(database_url)
    else:
        conn = psycopg.connect(
            dbname="gradcafe",
            user="lyuan"
        )

    records = load_json_data()
    create_table(conn)
    inserted = insert_data(conn,records)

    # check how many records were loaded
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM applicants;")
    count = cur.fetchone()[0]

    cur.close()
    conn.close()

    print(f"{inserted} records inserted.")


if __name__ == "__main__":
    main()