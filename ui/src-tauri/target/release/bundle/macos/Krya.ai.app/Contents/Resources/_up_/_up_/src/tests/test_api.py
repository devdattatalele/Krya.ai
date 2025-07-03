import pytest
from fastapi.testclient import TestClient
import os
import json
from unittest.mock import patch, MagicMock

# Import the FastAPI app
from app import app

# Create a test client
client = TestClient(app)

@pytest.fixture
def mock_config_file(tmp_path):
    """Create a mock config file for testing"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.json"
    config_data = {
        "api_key": "test_api_key",
        "model_name": "gemini-2.5-flash",
        "temperature": 1.0,
        "top_p": 0.9,
        "top_k": 40,
        "max_output_tokens": 1024
    }
    config_file.write_text(json.dumps(config_data))
    return str(config_file)

@pytest.fixture
def mock_env_file(tmp_path):
    """Create a mock .env file for testing"""
    env_file = tmp_path / ".env"
    env_file.write_text("GOOGLE_API_KEY=test_api_key")
    return str(env_file)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "online", "service": "Krya.ai API"}

@patch("app.load_config")
def test_get_config(mock_load_config):
    """Test the GET /config endpoint"""
    mock_load_config.return_value = {
        "api_key": "real_api_key",
        "model_name": "gemini-2.5-flash",
        "temperature": 1.0
    }
    
    response = client.get("/config")
    assert response.status_code == 200
    
    # Check that the API key is masked
    data = response.json()
    assert "api_key" in data
    assert data["api_key"].startswith("••••••••")
    assert data["api_key_set"] is True

@patch("app.save_config")
@patch("app.load_config")
def test_update_config(mock_load_config, mock_save_config):
    """Test the POST /config endpoint"""
    mock_load_config.return_value = {
        "api_key": "old_api_key",
        "model_name": "gemini-2.5-flash",
        "temperature": 1.0
    }
    mock_save_config.return_value = None
    
    response = client.post(
        "/config",
        json={
            "api_key": "new_api_key",
            "temperature": 0.8
        }
    )
    
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Configuration updated successfully"}
    
    # Check that save_config was called with the updated config
    mock_save_config.assert_called_once()
    called_config = mock_save_config.call_args[0][0]
    assert called_config["api_key"] == "new_api_key"
    assert called_config["temperature"] == 0.8
    assert called_config["model_name"] == "gemini-2.5-flash"  # Unchanged

@patch("app.execute_automation")
@patch("app.load_config")
def test_run_automation(mock_load_config, mock_execute_automation):
    """Test the POST /run endpoint"""
    mock_load_config.return_value = {"api_key": "test_api_key"}
    mock_execute_automation.return_value = None
    
    response = client.post(
        "/run",
        json={
            "prompt": "Generate a simple calculator app",
            "max_retries": 2
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "running"

@patch("app.load_config")
def test_run_automation_no_api_key(mock_load_config):
    """Test the POST /run endpoint with no API key"""
    mock_load_config.return_value = {"api_key": ""}
    
    response = client.post(
        "/run",
        json={
            "prompt": "Generate a simple calculator app"
        }
    )
    
    assert response.status_code == 400
    assert "API key not configured" in response.json()["detail"]

@patch("app.app_state.active_processes")
def test_stop_automation_not_found(mock_active_processes):
    """Test the POST /stop endpoint with a non-existent job ID"""
    mock_active_processes.__contains__.return_value = False
    
    response = client.post(
        "/stop",
        json={
            "job_id": "non-existent-id"
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

@patch("app.app_state.active_processes")
def test_stop_automation_success(mock_active_processes):
    """Test the POST /stop endpoint with a valid job ID"""
    # Mock process
    mock_process = MagicMock()
    mock_process.poll.return_value = None
    mock_process.terminate.return_value = None
    
    # Mock job info
    mock_job_info = {
        "status": "running",
        "process": mock_process
    }
    
    # Setup mock
    mock_active_processes.__contains__.return_value = True
    mock_active_processes.__getitem__.return_value = mock_job_info
    
    response = client.post(
        "/stop",
        json={
            "job_id": "valid-id"
        }
    )
    
    assert response.status_code == 200
    assert response.json() == {"status": "stopped", "job_id": "valid-id"}
    assert mock_job_info["status"] == "stopped"
    mock_process.terminate.assert_called_once()

@patch("app.app_state.active_processes")
@patch("app.app_state.recent_logs")
def test_get_status(mock_recent_logs, mock_active_processes):
    """Test the GET /status endpoint"""
    # Mock active processes
    mock_active_processes.values.return_value = [
        {"status": "running", "prompt": "test1", "start_time": "2023-01-01T00:00:00"},
        {"status": "completed", "prompt": "test2", "start_time": "2023-01-01T00:01:00"},
        {"status": "failed", "prompt": "test3", "start_time": "2023-01-01T00:02:00"}
    ]
    
    # Mock active jobs items
    mock_active_processes.items.return_value = [
        ("job1", {"status": "running", "prompt": "test1", "start_time": "2023-01-01T00:00:00"})
    ]
    
    # Mock recent logs
    mock_recent_logs.__getitem__.return_value = [
        {"level": "INFO", "message": "Test log"}
    ]
    
    response = client.get("/status")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "job_counts" in data
    assert "active_jobs" in data
    assert "recent_logs" in data
    assert data["job_counts"]["running"] == 1
    assert data["job_counts"]["completed"] == 1
    assert data["job_counts"]["failed"] == 1
    assert "job1" in data["active_jobs"] 