from unittest.mock import patch

import pytest
import psycopg

from app import create_app
from load_data import create_table, insert_data


def get_test_connection():
    return psycopg.connect(
        dbname="gradcafe_test",
        user="lyuan"
    )


def fake_records():
    return [
        {
            "program": "Computer Science, Johns Hopkins University",
            "comment": "Test comment",
            "date_added": "Jun 10, 2026",
            "entry_url": "https://example.com/integration/1",
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
            "entry_url": "https://example.com/integration/2",
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


def fake_analysis_results():
    return [
        {
            "question": "What percentage of test applications were accepted?",
            "result": ["50.00%"]
        }
    ]


@pytest.mark.integration
@patch("app.get_analysis_results")
@patch("app.refresh_database")
def test_pull_update_and_render_end_to_end(
    mock_refresh_database,
    mock_get_analysis_results
):
    conn = get_test_connection()
    create_table(conn)

    def fake_refresh():
        return insert_data(conn, fake_records())

    mock_refresh_database.side_effect = fake_refresh
    mock_get_analysis_results.side_effect = fake_analysis_results

    app = create_app()
    client = app.test_client()

    pull_response = client.post("/pull-data")
    pull_data = pull_response.get_json()

    assert pull_response.status_code == 200
    assert pull_data["ok"] is True
    assert pull_data["inserted_count"] == 2

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM applicants;")
    row_count = cur.fetchone()[0]

    assert row_count == 2

    update_response = client.post("/update-analysis")
    update_data = update_response.get_json()

    assert update_response.status_code == 200
    assert update_data["ok"] is True
    assert update_data["results"][0]["result"] == ["50.00%"]

    page_response = client.get("/analysis")
    html = page_response.data.decode("utf-8")

    assert page_response.status_code == 200
    assert "Answer:" in html
    assert "50.00%" in html

    cur.close()
    conn.close()


@pytest.mark.integration
@patch("app.refresh_database")
def test_multiple_pulls_with_overlapping_data_remain_unique(
    mock_refresh_database
):
    conn = get_test_connection()
    create_table(conn)

    first_batch = fake_records()

    second_batch = [
        fake_records()[0],
        {
            "program": "Data Science, Johns Hopkins University",
            "comment": "Third test comment",
            "date_added": "Jun 12, 2026",
            "entry_url": "https://example.com/integration/3",
            "applicant_status": "Accepted",
            "season": "Fall 2026",
            "student_type": "International",
            "gpa": "3.80",
            "gre_score": "318",
            "gre_v_score": "159",
            "gre_aw": "4.0",
            "degree": "Masters",
            "llm-generated-program": "Data Science",
            "llm-generated-university": "Johns Hopkins University",
        },
    ]

    mock_refresh_database.side_effect = [
        insert_data(conn, first_batch),
        insert_data(conn, second_batch),
    ]

    app = create_app()
    client = app.test_client()

    first_response = client.post("/pull-data")
    second_response = client.post("/pull-data")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.get_json()["inserted_count"] == 2
    assert second_response.get_json()["inserted_count"] == 1

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM applicants;")
    row_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    assert row_count == 3