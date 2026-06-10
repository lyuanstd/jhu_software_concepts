import pytest
import psycopg
from load_data import create_table, insert_data


def get_test_connection():
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