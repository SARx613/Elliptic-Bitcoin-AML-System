"""
Unit tests for recommendation functions (mocked Neo4j).
"""

from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from app.recommendation import (
    get_friend_counts,
    get_friend_recommendations,
    get_job_recommendations,
    get_people_you_may_know,
    pearson_correlation,
)


def test_pearson_correlation_positive():
    """Test Pearson correlation with positive correlation."""
    vec_a = np.array([1, 2, 3, 4, 5], dtype=float)
    vec_b = np.array([2, 4, 6, 8, 10], dtype=float)
    score = pearson_correlation(vec_a, vec_b)
    assert np.isclose(score, 1.0)


def test_pearson_correlation_negative():
    """Test Pearson correlation with negative correlation."""
    vec_a = np.array([1, 2, 3, 4, 5], dtype=float)
    vec_b = np.array([5, 4, 3, 2, 1], dtype=float)
    score = pearson_correlation(vec_a, vec_b)
    assert np.isclose(score, -1.0)


def test_pearson_correlation_zero():
    """Test Pearson correlation with zero correlation."""
    vec_a = np.array([1, 2, 3, 4, 5], dtype=float)
    vec_b = np.array([5, 1, 4, 2, 3], dtype=float)
    score = pearson_correlation(vec_a, vec_b)
    # Should be close to zero (no linear correlation)
    assert abs(score) < 0.5


def test_pearson_correlation_empty_vectors():
    """Test Pearson correlation with empty vectors."""
    vec_a = np.array([], dtype=float)
    vec_b = np.array([], dtype=float)
    with pytest.raises(ValueError):
        pearson_correlation(vec_a, vec_b)


def test_pearson_correlation_size_mismatch():
    """Test Pearson correlation with size mismatch."""
    vec_a = np.array([1, 2], dtype=float)
    vec_b = np.array([1, 2, 3], dtype=float)
    with pytest.raises(ValueError):
        pearson_correlation(vec_a, vec_b)


def test_pearson_correlation_zero_variance():
    """Test Pearson correlation with zero variance."""
    vec_a = np.array([1, 1, 1, 1], dtype=float)
    vec_b = np.array([1, 2, 3, 4], dtype=float)
    score = pearson_correlation(vec_a, vec_b)
    assert score == 0.0


@pytest.mark.asyncio
async def test_get_friend_recommendations():
    """Test get_friend_recommendations with mocked Neo4j."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()

    mock_records = [
        {"id": 2, "name": "Bob", "mutuals": 5},
        {"id": 3, "name": "Charlie", "mutuals": 3},
    ]
    mock_result.data = AsyncMock(return_value=mock_records)
    mock_session.run = AsyncMock(return_value=mock_result)

    result = await get_friend_recommendations(mock_session, user_id=1, limit=10)

    assert len(result) == 2
    assert result[0] == (2, "Bob", 5)
    assert result[1] == (3, "Charlie", 3)
    mock_session.run.assert_called_once()


@pytest.mark.asyncio
async def test_get_friend_recommendations_empty():
    """Test get_friend_recommendations with no results."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.data = AsyncMock(return_value=[])
    mock_session.run = AsyncMock(return_value=mock_result)

    result = await get_friend_recommendations(mock_session, user_id=1, limit=10)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_friend_counts():
    """Test get_friend_counts with mocked Neo4j."""
    mock_session = AsyncMock()

    # Mock direct friends query
    mock_result1 = AsyncMock()
    mock_record1 = MagicMock()
    mock_record1.__getitem__ = lambda self, key: {"cnt": 10}.get(key)
    mock_result1.single = AsyncMock(return_value=mock_record1)

    # Mock friends of friends query
    mock_result2 = AsyncMock()
    mock_record2 = MagicMock()
    mock_record2.__getitem__ = lambda self, key: {"cnt": 50}.get(key)
    mock_result2.single = AsyncMock(return_value=mock_record2)

    mock_session.run = AsyncMock(side_effect=[mock_result1, mock_result2])

    direct_count, fof_count = await get_friend_counts(mock_session, user_id=1)

    assert direct_count == 10
    assert fof_count == 50
    assert mock_session.run.call_count == 2


@pytest.mark.asyncio
async def test_get_friend_counts_no_results():
    """Test get_friend_counts when no results."""
    mock_session = AsyncMock()

    mock_result1 = AsyncMock()
    mock_result1.single = AsyncMock(return_value=None)
    mock_result2 = AsyncMock()
    mock_result2.single = AsyncMock(return_value=None)

    mock_session.run = AsyncMock(side_effect=[mock_result1, mock_result2])

    direct_count, fof_count = await get_friend_counts(mock_session, user_id=1)

    assert direct_count == 0
    assert fof_count == 0


@pytest.mark.asyncio
async def test_get_people_you_may_know():
    """Test get_people_you_may_know with mocked Neo4j."""
    mock_session = AsyncMock()

    # Mock user query
    mock_result1 = AsyncMock()
    mock_record1 = MagicMock()
    user_data = {"name": "Alice", "features": [1.0, 2.0, 3.0, 4.0]}
    mock_record1.__getitem__ = lambda self, key: user_data.get(key)
    mock_result1.single = AsyncMock(return_value=mock_record1)

    # Mock candidates query
    mock_result2 = AsyncMock()
    mock_records = [
        {"id": 2, "name": "Bob", "features": [2.0, 4.0, 6.0, 8.0]},  # Perfect correlation
        {"id": 3, "name": "Charlie", "features": [4.0, 3.0, 2.0, 1.0]},  # Negative correlation
    ]

    # Create mock records that can be iterated
    def make_mock_record(rec_data):
        mock_rec = MagicMock()
        mock_rec.__getitem__ = lambda self, key: rec_data.get(key)
        mock_rec.get = lambda key, default=None: rec_data.get(key, default)
        return mock_rec

    mock_record_objects = [make_mock_record(rec) for rec in mock_records]

    # Make result2 async iterable
    async def async_iter(self):
        for rec in mock_record_objects:
            yield rec

    mock_result2.__aiter__ = async_iter
    mock_session.run = AsyncMock(side_effect=[mock_result1, mock_result2])

    result = await get_people_you_may_know(mock_session, user_id=1, limit=10)

    assert len(result) == 2
    # Should be sorted by correlation descending
    assert result[0][0] == 2  # Bob has perfect correlation
    assert result[1][0] == 3  # Charlie has negative correlation


@pytest.mark.asyncio
async def test_get_people_you_may_know_no_features():
    """Test get_people_you_may_know when user has no features."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.single = AsyncMock(return_value=None)
    mock_session.run = AsyncMock(return_value=mock_result)

    result = await get_people_you_may_know(mock_session, user_id=1, limit=10)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_job_recommendations():
    """Test get_job_recommendations with mocked Neo4j."""
    mock_session = AsyncMock()

    # Mock user query
    mock_result1 = AsyncMock()
    mock_record1 = MagicMock()
    mock_record1.__getitem__ = lambda self, key: {"embedding": [1.0, 0.0, 0.0]}.get(key)
    mock_result1.single = AsyncMock(return_value=mock_record1)

    # Mock jobs query
    mock_result2 = AsyncMock()
    mock_records = [
        {
            "job_id": "job1",
            "title": "Engineer",
            "company": "Google",
            "location": "Paris",
            "job_posting_url": None,
            "normalized_salary": 100000.0,
            "embedding": [1.0, 0.0, 0.0],  # Perfect match
        },
        {
            "job_id": "job2",
            "title": "Developer",
            "company": "Microsoft",
            "location": None,
            "job_posting_url": None,
            "normalized_salary": None,
            "embedding": [0.0, 1.0, 0.0],  # Orthogonal (score = 0)
        },
    ]

    # Create mock records that can be iterated
    def make_mock_record(rec_data):
        mock_rec = MagicMock()
        mock_rec.__getitem__ = lambda self, key: rec_data.get(key)
        mock_rec.get = lambda key, default=None: rec_data.get(key, default)
        return mock_rec

    mock_record_objects = [make_mock_record(rec) for rec in mock_records]

    # Make result2 async iterable
    async def async_iter(self):
        for rec in mock_record_objects:
            yield rec

    mock_result2.__aiter__ = async_iter
    mock_session.run = AsyncMock(side_effect=[mock_result1, mock_result2])

    result = await get_job_recommendations(mock_session, user_id=1, limit=10)

    assert len(result) == 1  # Only job1 should be included (job2 has score 0)
    assert result[0][0] == "job1"
    assert result[0][1] == "Engineer"
    assert result[0][2] == "Google"
    assert np.isclose(result[0][5], 1.0)  # Perfect cosine similarity


@pytest.mark.asyncio
async def test_get_job_recommendations_no_embedding():
    """Test get_job_recommendations when user has no embedding."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_record = MagicMock()
    mock_record.__getitem__ = lambda self, key: None
    mock_result.single = AsyncMock(return_value=mock_record)
    mock_session.run = AsyncMock(return_value=mock_result)

    result = await get_job_recommendations(mock_session, user_id=1, limit=10)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_job_recommendations_empty_embedding():
    """Test get_job_recommendations when user has empty embedding."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_record = MagicMock()
    mock_record.__getitem__ = lambda self, key: {"embedding": []}.get(key)
    mock_result.single = AsyncMock(return_value=mock_record)
    mock_session.run = AsyncMock(return_value=mock_result)

    result = await get_job_recommendations(mock_session, user_id=1, limit=10)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_job_recommendations_size_mismatch():
    """Test get_job_recommendations with job embeddings of different size."""
    mock_session = AsyncMock()

    # Mock user query
    mock_result1 = AsyncMock()
    mock_record1 = MagicMock()
    mock_record1.__getitem__ = lambda self, key: {"embedding": [1.0, 0.0, 0.0]}.get(key)
    mock_result1.single = AsyncMock(return_value=mock_record1)

    # Mock jobs query with different sized embedding
    mock_result2 = AsyncMock()
    mock_records = [
        {
            "job_id": "job1",
            "title": "Engineer",
            "company": "Google",
            "location": None,
            "job_posting_url": None,
            "normalized_salary": None,
            "embedding": [1.0, 0.0],  # Different size
        },
    ]

    def make_mock_record(rec_data):
        mock_rec = MagicMock()
        mock_rec.__getitem__ = lambda self, key: rec_data.get(key)
        mock_rec.get = lambda key, default=None: rec_data.get(key, default)
        return mock_rec

    mock_record_objects = [make_mock_record(rec) for rec in mock_records]

    async def async_iter(self):
        for rec in mock_record_objects:
            yield rec

    mock_result2.__aiter__ = async_iter
    mock_session.run = AsyncMock(side_effect=[mock_result1, mock_result2])

    result = await get_job_recommendations(mock_session, user_id=1, limit=10)

    assert len(result) == 0  # Should skip jobs with different sized embeddings


@pytest.mark.asyncio
async def test_get_job_recommendations_zero_norm():
    """Test get_job_recommendations with zero norm vectors."""
    mock_session = AsyncMock()

    # Mock user query
    mock_result1 = AsyncMock()
    mock_record1 = MagicMock()
    mock_record1.__getitem__ = lambda self, key: {"embedding": [0.0, 0.0, 0.0]}.get(key)
    mock_result1.single = AsyncMock(return_value=mock_record1)

    # Mock jobs query
    mock_result2 = AsyncMock()
    mock_records = [
        {
            "job_id": "job1",
            "title": "Engineer",
            "company": None,
            "location": None,
            "job_posting_url": None,
            "normalized_salary": None,
            "embedding": [0.0, 0.0, 0.0],  # Zero norm
        },
    ]

    def make_mock_record(rec_data):
        mock_rec = MagicMock()
        mock_rec.__getitem__ = lambda self, key: rec_data.get(key)
        mock_rec.get = lambda key, default=None: rec_data.get(key, default)
        return mock_rec

    mock_record_objects = [make_mock_record(rec) for rec in mock_records]

    async def async_iter(self):
        for rec in mock_record_objects:
            yield rec

    mock_result2.__aiter__ = async_iter
    mock_session.run = AsyncMock(side_effect=[mock_result1, mock_result2])

    result = await get_job_recommendations(mock_session, user_id=1, limit=10)

    assert len(result) == 0  # Should skip zero norm vectors


@pytest.mark.asyncio
async def test_get_people_you_may_know_size_mismatch():
    """Test get_people_you_may_know with features of different sizes."""
    mock_session = AsyncMock()

    # Mock user query
    mock_result1 = AsyncMock()
    mock_record1 = MagicMock()
    user_data = {"name": "Alice", "features": [1.0, 2.0, 3.0, 4.0]}
    mock_record1.__getitem__ = lambda self, key: user_data.get(key)
    mock_result1.single = AsyncMock(return_value=mock_record1)

    # Mock candidates query with different sized features
    mock_result2 = AsyncMock()
    mock_records = [
        {"id": 2, "name": "Bob", "features": [2.0, 4.0]},  # Different size
        {"id": 3, "name": "Charlie", "features": [4.0, 3.0, 2.0, 1.0]},  # Same size
    ]

    def make_mock_record(rec_data):
        mock_rec = MagicMock()
        mock_rec.__getitem__ = lambda self, key: rec_data.get(key)
        mock_rec.get = lambda key, default=None: rec_data.get(key, default)
        return mock_rec

    mock_record_objects = [make_mock_record(rec) for rec in mock_records]

    async def async_iter(self):
        for rec in mock_record_objects:
            yield rec

    mock_result2.__aiter__ = async_iter
    mock_session.run = AsyncMock(side_effect=[mock_result1, mock_result2])

    result = await get_people_you_may_know(mock_session, user_id=1, limit=10)

    # Should only include Charlie (same size), skip Bob (different size)
    assert len(result) == 1
    assert result[0][0] == 3


@pytest.mark.asyncio
async def test_get_people_you_may_know_nan_score():
    """Test get_people_you_may_know filtering out NaN scores."""
    mock_session = AsyncMock()

    # Mock user query
    mock_result1 = AsyncMock()
    mock_record1 = MagicMock()
    user_data = {"name": "Alice", "features": [1.0, 2.0, 3.0, 4.0]}
    mock_record1.__getitem__ = lambda self, key: user_data.get(key)
    mock_result1.single = AsyncMock(return_value=mock_record1)

    # Mock candidates query
    mock_result2 = AsyncMock()
    mock_records = [
        {"id": 2, "name": "Bob", "features": [2.0, 4.0, 6.0, 8.0]},  # Valid correlation
    ]

    def make_mock_record(rec_data):
        mock_rec = MagicMock()
        mock_rec.__getitem__ = lambda self, key: rec_data.get(key)
        mock_rec.get = lambda key, default=None: rec_data.get(key, default)
        return mock_rec

    mock_record_objects = [make_mock_record(rec) for rec in mock_records]

    async def async_iter(self):
        for rec in mock_record_objects:
            yield rec

    mock_result2.__aiter__ = async_iter
    mock_session.run = AsyncMock(side_effect=[mock_result1, mock_result2])

    result = await get_people_you_may_know(mock_session, user_id=1, limit=10)

    assert len(result) == 1
    assert result[0][0] == 2
