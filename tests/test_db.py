"""
Unit tests for Neo4j database connection management.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db import get_driver, neo4j_session


def test_get_driver_creates_driver():
    """Test that get_driver creates a driver instance."""
    with patch("app.db._driver", None):
        with patch("app.db.AsyncGraphDatabase") as mock_driver_class:
            mock_driver = MagicMock()
            mock_driver_class.driver.return_value = mock_driver

            with patch("app.db.get_settings") as mock_get_settings:
                mock_settings = MagicMock()
                mock_settings.neo4j_uri = "bolt://test:7687"
                mock_settings.neo4j_user = "test_user"
                mock_settings.neo4j_password = "test_password"
                mock_get_settings.return_value = mock_settings

                driver = get_driver()

                mock_driver_class.driver.assert_called_once_with(
                    "bolt://test:7687",
                    auth=("test_user", "test_password"),
                )
                assert driver == mock_driver


def test_get_driver_caches_driver():
    """Test that get_driver caches the driver instance."""
    with patch("app.db._driver", None):
        with patch("app.db.AsyncGraphDatabase") as mock_driver_class:
            mock_driver = MagicMock()
            mock_driver_class.driver.return_value = mock_driver

            with patch("app.db.get_settings") as mock_get_settings:
                mock_settings = MagicMock()
                mock_settings.neo4j_uri = "bolt://test:7687"
                mock_settings.neo4j_user = "test_user"
                mock_settings.neo4j_password = "test_password"
                mock_get_settings.return_value = mock_settings

                driver1 = get_driver()
                driver2 = get_driver()

                # Should only be called once due to caching
                assert mock_driver_class.driver.call_count == 1
                assert driver1 is driver2


@pytest.mark.asyncio
async def test_neo4j_session_context_manager():
    """Test that neo4j_session works as an async context manager."""
    mock_driver = MagicMock()
    mock_session = AsyncMock()
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_session)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    mock_driver.session.return_value = mock_context

    with patch("app.db.get_driver", return_value=mock_driver):
        async with neo4j_session() as session:
            assert session == mock_session

        # Verify session was entered and exited
        mock_driver.session.assert_called_once()
        mock_context.__aenter__.assert_called_once()
        mock_context.__aexit__.assert_called_once()


@pytest.mark.asyncio
async def test_neo4j_session_yields_session():
    """Test that neo4j_session yields the session."""
    mock_driver = MagicMock()
    mock_session = AsyncMock()
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_session)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    mock_driver.session.return_value = mock_context

    with patch("app.db.get_driver", return_value=mock_driver):
        async with neo4j_session() as session:
            assert session is not None
            assert session == mock_session
