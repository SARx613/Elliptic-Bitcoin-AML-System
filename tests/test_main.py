"""
Unit tests for FastAPI main endpoints (mocked).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.main import (
    _run_count_query,
    debug_stats,
    recommend_friends,
    recommend_jobs,
    search_users,
    shortest_path,
    suggest_people,
)
from app.models import RecommendationResponse


@pytest.mark.asyncio
async def test_get_session():
    """Test get_session dependency."""
    from app.main import get_session

    mock_ctx = AsyncMock()
    mock_session_obj = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_session_obj)
    mock_ctx.__aexit__ = AsyncMock(return_value=None)

    with patch("app.main.neo4j_session", return_value=mock_ctx):
        async for session in get_session():
            assert session is not None
            assert session == mock_session_obj
            break


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint."""
    from app.main import health

    result = await health()
    assert result == {"status": "ok"}


@pytest.mark.asyncio
async def test_recommend_friends_success():
    """Test recommend_friends endpoint with successful response."""
    mock_session = AsyncMock()
    mock_recs = [(2, "Bob", 5), (3, "Charlie", 3)]

    with patch("app.main.get_friend_recommendations", return_value=mock_recs), \
         patch("app.main.get_friend_counts", return_value=(10, 50)):
        result = await recommend_friends(user_id=1, limit=10, session=mock_session)

        assert isinstance(result, RecommendationResponse)
        assert result.user.user_id == 1
        assert len(result.friends) == 2
        assert result.direct_friends_count == 10
        assert result.friends_of_friends_count == 50


@pytest.mark.asyncio
async def test_recommend_friends_no_results():
    """Test recommend_friends endpoint with no results."""
    from fastapi import HTTPException

    mock_session = AsyncMock()

    with patch("app.main.get_friend_recommendations", return_value=[]), \
         patch("app.main.get_friend_counts", return_value=(0, 0)):
        with pytest.raises(HTTPException) as exc_info:
            await recommend_friends(user_id=1, limit=10, session=mock_session)
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_suggest_people_success():
    """Test suggest_people endpoint with successful response."""
    mock_session = AsyncMock()
    mock_recs = [(2, "Bob", 0.95), (3, "Charlie", 0.85)]

    with patch("app.main.get_people_you_may_know", return_value=mock_recs):
        result = await suggest_people(user_id=1, limit=10, session=mock_session)

        assert isinstance(result, RecommendationResponse)
        assert result.user.user_id == 1
        assert len(result.people_you_may_know) == 2


@pytest.mark.asyncio
async def test_suggest_people_no_results():
    """Test suggest_people endpoint with no results."""
    from fastapi import HTTPException

    mock_session = AsyncMock()

    with patch("app.main.get_people_you_may_know", return_value=[]):
        with pytest.raises(HTTPException) as exc_info:
            await suggest_people(user_id=1, limit=10, session=mock_session)
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_recommend_jobs_success():
    """Test recommend_jobs endpoint with successful response."""
    mock_session = AsyncMock()
    mock_recs = [
        ("job1", "Engineer", "Google", "Paris", 100000.0, 0.95),
        ("job2", "Developer", "Microsoft", None, None, 0.85),
    ]

    with patch("app.main.get_job_recommendations", return_value=mock_recs):
        result = await recommend_jobs(user_id=1, limit=10, session=mock_session)

        assert isinstance(result, RecommendationResponse)
        assert result.user.user_id == 1
        assert len(result.jobs) == 2
        assert result.jobs[0].job_id == "job1"
        assert result.jobs[0].title == "Engineer"


@pytest.mark.asyncio
async def test_recommend_jobs_no_results():
    """Test recommend_jobs endpoint with no results."""
    from fastapi import HTTPException

    mock_session = AsyncMock()

    with patch("app.main.get_job_recommendations", return_value=[]):
        with pytest.raises(HTTPException) as exc_info:
            await recommend_jobs(user_id=1, limit=10, session=mock_session)
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_shortest_path_success():
    """Test shortest_path endpoint with successful response."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_record = MagicMock()
    mock_record.__getitem__ = lambda self, key: {"path": [1, 2, 3, 4]}.get(key)
    mock_result.single = AsyncMock(return_value=mock_record)
    mock_session.run = AsyncMock(return_value=mock_result)

    result = await shortest_path(from_user=1, to_user=4, session=mock_session)

    assert result == {"path": [1, 2, 3, 4]}


@pytest.mark.asyncio
async def test_shortest_path_no_path():
    """Test shortest_path endpoint with no path found."""
    from fastapi import HTTPException

    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.single = AsyncMock(return_value=None)
    mock_session.run = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as exc_info:
        await shortest_path(from_user=1, to_user=999, session=mock_session)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_search_users():
    """Test search_users endpoint."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_records = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
    mock_result.data = AsyncMock(return_value=mock_records)
    mock_session.run = AsyncMock(return_value=mock_result)

    result = await search_users(q="alice", limit=5, session=mock_session)

    assert len(result) == 2
    assert result[0].user_id == 1
    assert result[0].name == "Alice"


@pytest.mark.asyncio
async def test_debug_stats_success():
    """Test debug_stats endpoint with successful connection."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_record = MagicMock()
    mock_record.__getitem__ = lambda self, key: {"cnt": 10}.get(key)
    mock_result.single = AsyncMock(return_value=mock_record)
    mock_result.data = AsyncMock(return_value=[{"id": 1, "name": "Alice"}])
    mock_session.run = AsyncMock(return_value=mock_result)

    with patch("app.main.get_settings") as mock_settings:
        mock_settings.return_value.neo4j_uri = "bolt://test:7687"
        result = await debug_stats(session=mock_session)

        assert result["connection_ok"] is True
        assert "user_count" in result


@pytest.mark.asyncio
async def test_debug_stats_connection_error():
    """Test debug_stats endpoint with connection error."""
    from neo4j.exceptions import ServiceUnavailable

    mock_session = AsyncMock()
    mock_session.run = AsyncMock(side_effect=ServiceUnavailable("Connection failed"))

    with patch("app.main.get_settings") as mock_settings:
        mock_settings.return_value.neo4j_uri = "bolt://test:7687"
        result = await debug_stats(session=mock_session)

        assert result["connection_ok"] is False
        assert "error" in result


@pytest.mark.asyncio
async def test_debug_stats_generic_exception():
    """Test debug_stats endpoint with generic exception."""
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(side_effect=ValueError("Unexpected error"))

    with patch("app.main.get_settings") as mock_settings:
        mock_settings.return_value.neo4j_uri = "bolt://test:7687"
        result = await debug_stats(session=mock_session)

        assert result["connection_ok"] is False
        assert "error" in result


@pytest.mark.asyncio
async def test_debug_stats_sample_users_error():
    """Test debug_stats endpoint with error in sample users query."""
    from neo4j.exceptions import ServiceUnavailable

    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_record = MagicMock()
    mock_record.__getitem__ = lambda self, key: {"cnt": 10}.get(key)
    mock_result.single = AsyncMock(return_value=mock_record)
    mock_result.data = AsyncMock(return_value=[{"id": 1, "name": "Alice"}])

    # First call succeeds (test query), count queries succeed, sample query fails
    call_count = 0
    def run_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # Test query succeeds
            return mock_result
        elif call_count <= 7:
            # Count queries succeed
            return mock_result
        else:
            # Sample users query fails with ServiceUnavailable
            raise ServiceUnavailable("Error fetching users")
    mock_session.run = AsyncMock(side_effect=run_side_effect)

    with patch("app.main.get_settings") as mock_settings:
        mock_settings.return_value.neo4j_uri = "bolt://test:7687"
        result = await debug_stats(session=mock_session)

        assert result["connection_ok"] is True
        assert "sample_users_error" in result


@pytest.mark.asyncio
async def test_debug_stats_sample_users_generic_error():
    """Test debug_stats endpoint with generic error in sample users query."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_record = MagicMock()
    mock_record.__getitem__ = lambda self, key: {"cnt": 10}.get(key)
    mock_result.single = AsyncMock(return_value=mock_record)
    mock_result.data = AsyncMock(return_value=[{"id": 1, "name": "Alice"}])

    # First call succeeds (test query), count queries succeed, sample query fails
    call_count = 0
    def run_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # Test query succeeds
            return mock_result
        elif call_count <= 7:
            # Count queries succeed
            return mock_result
        else:
            # Sample users query fails with generic exception
            raise ValueError("Unexpected error")
    mock_session.run = AsyncMock(side_effect=run_side_effect)

    with patch("app.main.get_settings") as mock_settings:
        mock_settings.return_value.neo4j_uri = "bolt://test:7687"
        result = await debug_stats(session=mock_session)

        assert result["connection_ok"] is True
        assert "sample_users_error" in result


@pytest.mark.asyncio
async def test_run_count_query_success():
    """Test _run_count_query helper function."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_record = MagicMock()
    mock_record.__getitem__ = lambda self, key: {"cnt": 42}.get(key)
    mock_result.single = AsyncMock(return_value=mock_record)
    mock_session.run = AsyncMock(return_value=mock_result)

    result = await _run_count_query(mock_session, "MATCH (n) RETURN count(n) AS cnt", "test_count")

    assert result == {"test_count": 42}


@pytest.mark.asyncio
async def test_run_count_query_no_record():
    """Test _run_count_query with no record returned."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.single = AsyncMock(return_value=None)
    mock_session.run = AsyncMock(return_value=mock_result)

    result = await _run_count_query(mock_session, "MATCH (n) RETURN count(n) AS cnt", "test_count")

    assert result == {"test_count": 0}


@pytest.mark.asyncio
async def test_run_count_query_error():
    """Test _run_count_query with error."""
    from neo4j.exceptions import ServiceUnavailable

    mock_session = AsyncMock()
    mock_session.run = AsyncMock(side_effect=ServiceUnavailable("Error"))

    result = await _run_count_query(mock_session, "MATCH (n) RETURN count(n) AS cnt", "test_count")

    assert "test_count_error" in result


@pytest.mark.asyncio
async def test_run_count_query_generic_exception():
    """Test _run_count_query with generic exception."""
    mock_session = AsyncMock()
    mock_session.run = AsyncMock(side_effect=ValueError("Unexpected error"))

    result = await _run_count_query(mock_session, "MATCH (n) RETURN count(n) AS cnt", "test_count")

    assert "test_count_error" in result


@pytest.mark.asyncio
async def test_index_endpoint():
    """Test index endpoint returns HTML."""
    from app.main import index

    result = await index()
    assert isinstance(result, str)
    assert "Professional Social Graph Explorer" in result
    assert "<!DOCTYPE html>" in result

