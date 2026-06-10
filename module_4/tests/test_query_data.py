from decimal import Decimal
from unittest.mock import Mock, patch
import pytest
from query_data import (
    format_value,
    format_row,
    get_queries,
    get_connection,
    main,
    run_query
)

def test_format_value_converts_decimal_to_string():
    value = Decimal("3.79")
    result = format_value(value)
    assert result == "3.79"

def test_format_value_converts_integer_to_string():
    value = 33040
    result = format_value(value)
    assert result == "33040"

def test_format_value_converts_none_to_string():
    value = None
    result = format_value(value)
    assert result == "None"

def test_format_row_joins_multiple_values():
    row = ("Johns Hopkins University", 18, Decimal("35.83"))
    result = format_row(row)
    assert result == "Johns Hopkins University, 18, 35.83"

def test_get_queries_returns_list_of_query_dicts():
    queries = get_queries()

    assert isinstance(queries, list)
    assert len(queries) > 0
    assert "question" in queries[0]
    assert "sql" in queries[0]


@pytest.mark.analysis
@patch("query_data.psycopg.connect")
def test_get_connection_uses_database_url(mock_connect, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test-url")
    get_connection()
    mock_connect.assert_called_once_with("postgresql://test-url")


@pytest.mark.analysis
@patch("query_data.psycopg.connect")
def test_get_connection_uses_local_database_when_no_database_url(
    mock_connect,
    monkeypatch
):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_connection()
    mock_connect.assert_called_once_with(
        dbname="gradcafe",
        user="lyuan"
    )


@pytest.mark.analysis
def test_run_query_formats_and_returns_results():
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        ("Johns Hopkins University", 18),
        ("Acceptance Rate", "35.83%"),
    ]

    mock_conn = Mock()
    mock_conn.cursor.return_value = mock_cursor

    result = run_query(
        mock_conn,
        "Test Question",
        "SELECT * FROM applicants;"
    )

    assert result == [
        "Johns Hopkins University, 18",
        "Acceptance Rate, 35.83%",
    ]

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM applicants;"
    )
    mock_cursor.close.assert_called_once()


@pytest.mark.analysis
@patch("query_data.run_query")
@patch("query_data.get_queries")
@patch("query_data.get_connection")
def test_main_runs_all_queries_and_closes_connection(
    mock_get_connection,
    mock_get_queries,
    mock_run_query
):
    mock_conn = Mock()
    mock_get_connection.return_value = mock_conn

    mock_get_queries.return_value = [
        {
            "question": "Question 1",
            "sql": "SELECT 1;"
        },
        {
            "question": "Question 2",
            "sql": "SELECT 2;"
        },
    ]

    main()

    assert mock_run_query.call_count == 2
    mock_conn.close.assert_called_once()