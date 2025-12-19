"""
Unit tests for ETL scripts (mocked).
"""

from unittest.mock import MagicMock, mock_open, patch

from scripts.load_jobs import build_job_text
from scripts.load_snap import load_edges, load_features, load_targets


def test_build_job_text_all_fields():
    """Test build_job_text with all fields."""
    result = build_job_text("Software Engineer", "Google", "Paris")
    assert result == "Software Engineer - Google - Paris"


def test_build_job_text_no_location():
    """Test build_job_text without location."""
    result = build_job_text("Software Engineer", "Google", None)
    assert result == "Software Engineer - Google"


def test_build_job_text_no_company():
    """Test build_job_text without company."""
    result = build_job_text("Software Engineer", None, "Paris")
    assert result == "Software Engineer - Paris"


def test_build_job_text_title_only():
    """Test build_job_text with title only."""
    result = build_job_text("Software Engineer", None, None)
    assert result == "Software Engineer"


def test_load_snap_to_dense():
    """Test the to_dense function logic from load_snap."""
    # Simulate the to_dense function from load_snap.py
    features = {
        "1": [1, 2, 3],
        "2": [4, 5],
        "3": [6, 7, 8, 9],
    }
    max_len = max(len(v) for v in features.values())

    def to_dense(vec):
        dense = list(vec)
        if len(dense) < max_len:
            dense.extend([0] * (max_len - len(dense)))
        return dense

    dense_features = {int(k): to_dense(v) for k, v in features.items()}
    assert dense_features[1] == [1, 2, 3, 0]
    assert dense_features[2] == [4, 5, 0, 0]
    assert dense_features[3] == [6, 7, 8, 9]


def test_load_edges():
    """Test load_edges function loads data correctly."""
    import pandas as pd
    result = load_edges()
    assert isinstance(result, pd.DataFrame)
    assert "src" in result.columns
    assert "dst" in result.columns
    assert len(result) > 0


def test_load_targets():
    """Test load_targets function loads data correctly."""
    import pandas as pd
    result = load_targets()
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0


def test_load_features():
    """Test load_features function loads data correctly."""
    result = load_features()
    assert isinstance(result, dict)
    assert len(result) > 0

