"""Tests for the run.py script."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def run_module():
    """Import the run module and clean up after the test."""
    # Add scripts directory to path temporarily
    scripts_dir = Path(__file__).parent.parent / "scripts"
    sys.path.insert(0, str(scripts_dir))

    try:
        import run  # pyright: ignore

        yield run
    finally:
        # Clean up sys.path
        sys.path.pop(0)
        # Remove the imported module
        if "run" in sys.modules:
            del sys.modules["run"]


@patch.dict(
    os.environ, {"DATABASE_URL": "postgresql://postgres:postgres@localhost:5433/test"}
)
@patch("run.sum_and_pivot")
@patch("run.psycopg2.connect")
def test_run_script_main_function(
    mock_connect,
    mock_pivot,
    run_module,
):
    """Test the main function from run.py by importing it directly."""
    # Setup mocks
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_pivot.return_value = {"category": "value1", "total": 100}

    # Call main
    result = run_module.main()

    # Verify the function was called correctly
    mock_connect.assert_called_once()
    mock_pivot.assert_called_once_with(mock_conn, verbose=True)
    assert result == {"category": "value1", "total": 100}
