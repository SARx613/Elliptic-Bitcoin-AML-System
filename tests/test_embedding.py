"""
Unit tests for the embedding projection utilities.
"""

import numpy as np

from app.embedding import JOB_EMBED_DIM, project_features_to_embedding


def test_project_features_empty_list():
    """Test projection with empty features list."""
    result = project_features_to_embedding([])
    assert len(result) == JOB_EMBED_DIM
    assert all(x == 0.0 for x in result)


def test_project_features_exact_dimension():
    """Test projection when features match exactly the target dimension."""
    features = [1.0, 2.0, 3.0] * (JOB_EMBED_DIM // 3)
    result = project_features_to_embedding(features)
    assert len(result) == JOB_EMBED_DIM
    # Should be normalized
    norm = np.linalg.norm(result)
    assert np.isclose(norm, 1.0, atol=1e-6)


def test_project_features_shorter_than_dim():
    """Test projection when features are shorter than target dimension."""
    features = [1.0, 2.0, 3.0]
    result = project_features_to_embedding(features, dim=10)
    assert len(result) == 10
    # First 3 should be normalized, rest should be zeros
    norm_first_3 = np.linalg.norm(result[:3])
    assert np.isclose(norm_first_3, 1.0, atol=1e-6)
    assert all(x == 0.0 for x in result[3:])


def test_project_features_longer_than_dim():
    """Test projection when features are longer than target dimension."""
    features = list(range(500))  # Longer than JOB_EMBED_DIM (384)
    result = project_features_to_embedding(features)
    assert len(result) == JOB_EMBED_DIM
    # After truncation, norm should be <= 1.0 (normalized before truncation)
    norm = np.linalg.norm(result)
    assert norm <= 1.0 + 1e-6  # Allow small floating point errors
    assert norm > 0.0  # Should not be zero


def test_project_features_custom_dimension():
    """Test projection with custom dimension."""
    features = [1.0, 2.0, 3.0]
    result = project_features_to_embedding(features, dim=5)
    assert len(result) == 5


def test_project_features_normalization():
    """Test that features are properly normalized."""
    features = [3.0, 4.0]  # Vector with norm 5
    result = project_features_to_embedding(features, dim=2)
    assert len(result) == 2
    # Should be normalized to unit vector
    norm = np.linalg.norm(result)
    assert np.isclose(norm, 1.0, atol=1e-6)
    # Check normalized values
    assert np.isclose(result[0], 3.0 / 5.0, atol=1e-6)
    assert np.isclose(result[1], 4.0 / 5.0, atol=1e-6)


def test_project_features_zero_vector():
    """Test projection with zero vector."""
    features = [0.0, 0.0, 0.0]
    result = project_features_to_embedding(features, dim=5)
    assert len(result) == 5
    # Zero vector should remain zeros (no normalization when norm is 0)
    assert all(x == 0.0 for x in result)


def test_project_features_from_tuple():
    """Test that function accepts tuples, not just lists."""
    features = (1.0, 2.0, 3.0)
    result = project_features_to_embedding(features, dim=5)
    assert len(result) == 5
    assert isinstance(result, list)


def test_project_features_from_numpy_array():
    """Test that function accepts numpy arrays."""
    features = np.array([1.0, 2.0, 3.0])
    result = project_features_to_embedding(features, dim=5)
    assert len(result) == 5
    assert isinstance(result, list)
