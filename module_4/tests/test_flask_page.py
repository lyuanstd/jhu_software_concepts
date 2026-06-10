from unittest.mock import patch
import pytest
from app import create_app


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


