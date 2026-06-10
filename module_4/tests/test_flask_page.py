from unittest.mock import Mock, patch
import pytest
from app import create_app, get_analysis_results


@pytest.mark.web
@patch("app.get_analysis_results")
def test_analysis_page_returns_200(mock_get_analysis_results):
    mock_get_analysis_results.return_value = []

    app = create_app()
    client = app.test_client()

    response = client.get("/analysis")

    assert response.status_code == 200


@pytest.mark.web
@patch("app.get_analysis_results")
def test_analysis_page_contains_required_text(mock_get_analysis_results):
    mock_get_analysis_results.return_value = [
        {
            "question": "Test Question",
            "result": ["Test Answer"]
        }
    ]

    app = create_app()
    client = app.test_client()

    response = client.get("/analysis")

    assert b"Analysis" in response.data
    assert b"Pull Data" in response.data
    assert b"Update Analysis" in response.data
    assert b"Answer:" in response.data


@pytest.mark.web
def test_home_redirects_to_analysis():
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 302
    assert response.headers["Location"] == "/analysis"


@pytest.mark.web
@patch("app.get_queries")
@patch("app.run_query")
@patch("app.get_connection")
def test_get_analysis_results_runs_queries_and_closes_connection(
    mock_get_connection,
    mock_run_query,
    mock_get_queries
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

    mock_run_query.side_effect = [
        ["Result 1"],
        ["Result 2"],
    ]

    results = get_analysis_results()

    assert results == [
        {
            "question": "Question 1",
            "result": ["Result 1"]
        },
        {
            "question": "Question 2",
            "result": ["Result 2"]
        },
    ]

    assert mock_run_query.call_count == 2
    mock_conn.close.assert_called_once()


@pytest.mark.buttons
@patch("app.refresh_database")
def test_post_pull_data_returns_500_when_refresh_fails(
    mock_refresh_database
):
    mock_refresh_database.side_effect = Exception("Database error")

    app = create_app()
    client = app.test_client()

    response = client.post("/pull-data")
    data = response.get_json()

    assert response.status_code == 500
    assert data["ok"] is False
    assert data["error"] == "Database error"