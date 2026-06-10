import json
from datetime import date
from unittest.mock import Mock, patch
import pytest
import psycopg
import refresh_data
import os
from load_data import (
    create_table,
    insert_data,
    get_database_url,
    load_json_data,
    parse_date,
    parse_float,
    create_table_if_not_exists,
)


def get_test_connection():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg.connect(database_url)
    return psycopg.connect(
        dbname="gradcafe_test",
        user="lyuan"
    )


def sample_records():
    return [
        {
            "program": "Computer Science, Johns Hopkins University",
            "comment": "Test comment",
            "date_added": "Jun 10, 2026",
            "entry_url": "https://example.com/applicant/1",
            "applicant_status": "Accepted",
            "season": "Fall 2026",
            "student_type": "American",
            "gpa": "3.90",
            "gre_score": "320",
            "gre_v_score": "160",
            "gre_aw": "4.5",
            "degree": "Masters",
            "llm-generated-program": "Computer Science",
            "llm-generated-university": "Johns Hopkins University",
        },
        {
            "program": "Artificial Intelligence, Johns Hopkins University",
            "comment": "Another test comment",
            "date_added": "Jun 11, 2026",
            "entry_url": "https://example.com/applicant/2",
            "applicant_status": "Rejected",
            "season": "Fall 2026",
            "student_type": "International",
            "gpa": "3.75",
            "gre_score": "315",
            "gre_v_score": "158",
            "gre_aw": "4.0",
            "degree": "Masters",
            "llm-generated-program": "Artificial Intelligence",
            "llm-generated-university": "Johns Hopkins University",
        },
    ]


@pytest.mark.db
def test_insert_data_adds_rows_with_required_fields():
    conn = get_test_connection()
    create_table(conn)

    inserted_count = insert_data(conn, sample_records())

    cur = conn.cursor()
    cur.execute("""
        SELECT
            program,
            date_added,
            url,
            status,
            term,
            degree,
            us_or_international,
            llm_generated_program,
            llm_generated_university
        FROM applicants
        ORDER BY url;
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    assert inserted_count == 2
    assert len(rows) == 2

    for row in rows:
        (
            program,
            date_added,
            url,
            status,
            term,
            degree,
            us_or_international,
            llm_generated_program,
            llm_generated_university,
        ) = row

        assert program is not None
        assert date_added is not None
        assert url is not None
        assert status is not None
        assert term is not None
        assert degree is not None
        assert us_or_international is not None
        assert llm_generated_program is not None
        assert llm_generated_university is not None


@pytest.mark.db
def test_insert_data_is_idempotent_for_duplicate_urls():
    conn = get_test_connection()
    create_table(conn)

    first_insert_count = insert_data(conn, sample_records())
    second_insert_count = insert_data(conn, sample_records())

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM applicants;")
    row_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    assert first_insert_count == 2
    assert second_insert_count == 0
    assert row_count == 2


@pytest.mark.db
def test_query_result_has_expected_template_keys():
    query_result = {
        "question": "How many entries are for Fall 2026?",
        "result": ["2"]
    }

    assert "question" in query_result
    assert "result" in query_result


@pytest.mark.db
def test_get_database_url_reads_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test-url")

    assert get_database_url() == "postgresql://test-url"


@pytest.mark.db
def test_load_json_data_reads_json_file(tmp_path):
    test_file = tmp_path / "data.json"
    test_data = [{"program": "Computer Science"}]
    test_file.write_text(json.dumps(test_data), encoding="utf-8")
    result = load_json_data(test_file)

    assert result == test_data


@pytest.mark.db
def test_parse_date_valid_date():
    assert parse_date("Jun 10, 2026") == date(2026, 6, 10)


@pytest.mark.db
def test_parse_date_empty_value():
    assert parse_date("") is None


@pytest.mark.db
def test_parse_date_invalid_format():
    assert parse_date("2026-06-10") is None


@pytest.mark.db
def test_parse_float_valid_number():
    assert parse_float("3.75") == 3.75


@pytest.mark.db
def test_parse_float_none():
    assert parse_float(None) is None


@pytest.mark.db
def test_parse_float_invalid_value():
    assert parse_float("not-a-number") is None


@pytest.mark.db
@patch("refresh_data.psycopg.connect")
@patch("refresh_data.subprocess.run")
def test_refresh_database_uses_database_url(
    mock_subprocess_run,
    mock_connect,
    monkeypatch
):
    fake_scrape_data = Mock()
    fake_load_json_data = Mock(return_value=[{"entry_url": "url-1"}])
    fake_create_table_if_not_exists = Mock()
    fake_insert_data = Mock(return_value=1)

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "scrape":
            fake_scrape_module = Mock()
            fake_scrape_module.scrape_data = fake_scrape_data
            return fake_scrape_module

        if name == "load_data":
            fake_load_data_module = Mock()
            fake_load_data_module.CLEAN_DATA_PATH = "clean-data-path"
            fake_load_data_module.create_table_if_not_exists = (
                fake_create_table_if_not_exists
            )
            fake_load_data_module.insert_data = fake_insert_data
            fake_load_data_module.load_json_data = fake_load_json_data
            return fake_load_data_module

        return original_import(
            name,
            globals,
            locals,
            fromlist,
            level
        )

    original_import = __import__

    monkeypatch.setenv("DATABASE_URL", "postgresql://test-url")
    monkeypatch.setattr("builtins.__import__", fake_import)

    fake_conn = Mock()
    mock_connect.return_value = fake_conn

    inserted_count = refresh_data.refresh_database()

    assert inserted_count == 1

    fake_scrape_data.assert_called_once_with(
        max_pages=3,
        use_progress=False
    )

    mock_subprocess_run.assert_called_once()
    fake_load_json_data.assert_called_once_with("clean-data-path")
    mock_connect.assert_called_once_with("postgresql://test-url")
    fake_create_table_if_not_exists.assert_called_once_with(fake_conn)
    fake_insert_data.assert_called_once_with(
        fake_conn,
        [{"entry_url": "url-1"}]
    )
    fake_conn.close.assert_called_once()


@pytest.mark.db
@patch("refresh_data.psycopg.connect")
@patch("refresh_data.subprocess.run")
def test_refresh_database_uses_local_database_when_no_database_url(
    mock_subprocess_run,
    mock_connect,
    monkeypatch
):
    fake_scrape_data = Mock()
    fake_load_json_data = Mock(return_value=[])
    fake_create_table_if_not_exists = Mock()
    fake_insert_data = Mock(return_value=0)

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "scrape":
            fake_scrape_module = Mock()
            fake_scrape_module.scrape_data = fake_scrape_data
            return fake_scrape_module

        if name == "load_data":
            fake_load_data_module = Mock()
            fake_load_data_module.CLEAN_DATA_PATH = "clean-data-path"
            fake_load_data_module.create_table_if_not_exists = (
                fake_create_table_if_not_exists
            )
            fake_load_data_module.insert_data = fake_insert_data
            fake_load_data_module.load_json_data = fake_load_json_data
            return fake_load_data_module

        return original_import(
            name,
            globals,
            locals,
            fromlist,
            level
        )

    original_import = __import__

    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("builtins.__import__", fake_import)

    fake_conn = Mock()
    mock_connect.return_value = fake_conn

    inserted_count = refresh_data.refresh_database()

    assert inserted_count == 0

    mock_connect.assert_called_once_with(
        dbname="gradcafe",
        user="lyuan"
    )
    fake_conn.close.assert_called_once()


@pytest.mark.db
def test_create_table_if_not_exists_creates_applicants_table():
    conn = get_test_connection()

    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS applicants;")
    conn.commit()

    create_table_if_not_exists(conn)

    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_name='applicants'
    """)

    result = cur.fetchone()

    assert result is not None

    cur.close()
    conn.close()


@pytest.mark.db
def test_create_table_if_not_exists_is_safe_to_run_twice():
    conn = get_test_connection()

    create_table_if_not_exists(conn)
    create_table_if_not_exists(conn)

    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name='applicants'
    """)

    count = cur.fetchone()[0]

    assert count == 1

    cur.close()
    conn.close()