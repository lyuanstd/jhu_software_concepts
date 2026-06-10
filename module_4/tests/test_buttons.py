from unittest.mock import patch
import pytest
from bs4 import BeautifulSoup
from app import create_app


@pytest.mark.buttons
@patch("app.get_analysis_results")
def test_pull_data_button_exists(mock_get_analysis_results):
    mock_get_analysis_results.return_value = []

    app = create_app()
    client = app.test_client()

    response = client.get("/analysis")
    soup = BeautifulSoup(response.data, "html.parser")

    button = soup.find("button", attrs={"data-testid": "pull-data-btn"})

    assert response.status_code == 200
    assert button is not None
    assert button.get_text(strip=True) == "Pull Data"


@pytest.mark.buttons
@patch("app.get_analysis_results")
def test_update_analysis_button_exists(mock_get_analysis_results):
    mock_get_analysis_results.return_value = []

    app = create_app()
    client = app.test_client()

    response = client.get("/analysis")
    soup = BeautifulSoup(response.data, "html.parser")

    button = soup.find("button", attrs={"data-testid": "update-analysis-btn"})

    assert response.status_code == 200
    assert button is not None
    assert button.get_text(strip=True) == "Update Analysis"


@pytest.mark.buttons
@patch("app.get_analysis_results")
def test_pull_data_form_posts_to_correct_route(mock_get_analysis_results):
    mock_get_analysis_results.return_value = []

    app = create_app()
    client = app.test_client()

    response = client.get("/analysis")
    soup = BeautifulSoup(response.data, "html.parser")

    form = soup.find("form", attrs={"action": "/pull-data", "method": "post"})

    assert response.status_code == 200
    assert form is not None


@pytest.mark.buttons
@patch("app.get_analysis_results")
def test_update_analysis_form_posts_to_correct_route(mock_get_analysis_results):
    mock_get_analysis_results.return_value = []

    app = create_app()
    client = app.test_client()

    response = client.get("/analysis")
    soup = BeautifulSoup(response.data, "html.parser")

    form = soup.find("form", attrs={"action": "/update-analysis", "method": "post"})

    assert response.status_code == 200
    assert form is not None


@pytest.mark.buttons
@patch("app.refresh_database")
def test_post_pull_data_returns_ok_when_not_busy(mock_refresh_database):
    mock_refresh_database.return_value = 3

    app = create_app()
    client = app.test_client()

    response = client.post("/pull-data")
    data = response.get_json()

    assert response.status_code == 200
    assert data["ok"] is True
    assert data["inserted_count"] == 3
    mock_refresh_database.assert_called_once()


@pytest.mark.buttons
@patch("app.get_analysis_results")
def test_post_update_analysis_returns_ok_when_not_busy(mock_get_analysis_results):
    mock_get_analysis_results.return_value = [
        {
            "question": "Test Question",
            "result": ["Test Answer"]
        }
    ]

    app = create_app()
    client = app.test_client()

    response = client.post("/update-analysis")
    data = response.get_json()

    assert response.status_code == 200
    assert data["ok"] is True
    assert "results" in data
    assert data["results"][0]["question"] == "Test Question"
    mock_get_analysis_results.assert_called_once()


@pytest.mark.buttons
@patch("app.get_analysis_results")
def test_update_analysis_returns_409_when_busy(mock_get_analysis_results):
    app = create_app({
        "IS_PULLING_DATA": True
    })

    client = app.test_client()

    response = client.post("/update-analysis")
    data = response.get_json()

    assert response.status_code == 409
    assert data["busy"] is True

    mock_get_analysis_results.assert_not_called()


@pytest.mark.buttons
@patch("app.refresh_database")
def test_pull_data_returns_409_when_busy(mock_refresh_database):
    app = create_app({
        "IS_PULLING_DATA": True
    })

    client = app.test_client()

    response = client.post("/pull-data")
    data = response.get_json()

    assert response.status_code == 409
    assert data["busy"] is True

    mock_refresh_database.assert_not_called()