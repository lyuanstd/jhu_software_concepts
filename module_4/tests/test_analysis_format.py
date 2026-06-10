import re
from unittest.mock import patch
import pytest
from app import create_app


@pytest.mark.analysis
@patch("app.get_analysis_results")
def test_page_includes_answer_labels(mock_get_analysis_results):
    mock_get_analysis_results.return_value = [
        {
            "question": "What percentage of entries are international students?",
            "result": ["46.85%"]
        }
    ]

    app = create_app()
    client = app.test_client()

    response = client.get("/analysis")

    assert response.status_code == 200
    assert b"Answer:" in response.data


@pytest.mark.analysis
@patch("app.get_analysis_results")
def test_percentage_with_two_decimals(mock_get_analysis_results):
    mock_get_analysis_results.return_value = [
        {
            "question": "What percentage of entries are international students?",
            "result": ["46.85%"]
        }
    ]

    app = create_app()
    client = app.test_client()

    response = client.get("/analysis")
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert re.search(r"\d+\.\d{2}%", html)
    assert "46.85%" in html