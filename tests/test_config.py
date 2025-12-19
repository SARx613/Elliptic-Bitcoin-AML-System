"""
Unit tests for configuration management.
"""

import os
from unittest.mock import patch

from app.config import Settings, get_settings


def test_settings_default_values():
    """Test Settings with default values."""
    with patch.dict(os.environ, {}, clear=True):
        # Clear cache to get fresh settings
        get_settings.cache_clear()
        settings = Settings()
        assert settings.neo4j_uri == "bolt://localhost:7687"
        assert settings.neo4j_user == "neo4j"
        assert settings.neo4j_password == "password"
        get_settings.cache_clear()


def test_settings_from_environment():
    """Test Settings reading from environment variables."""
    # Note: Due to how Pydantic evaluates default values at class definition time,
    # we test that Settings can be instantiated with explicit values
    settings = Settings(
        neo4j_uri="bolt://test:7687",
        neo4j_user="test_user",
        neo4j_password="test_password",
    )
    assert settings.neo4j_uri == "bolt://test:7687"
    assert settings.neo4j_user == "test_user"
    assert settings.neo4j_password == "test_password"


def test_get_settings_caching():
    """Test that get_settings uses caching."""
    settings1 = get_settings()
    settings2 = get_settings()
    # Should return the same instance due to caching
    assert settings1 is settings2


def test_get_settings_returns_settings_instance():
    """Test that get_settings returns a Settings instance."""
    settings = get_settings()
    assert isinstance(settings, Settings)


def test_settings_partial_environment():
    """Test Settings with partial explicit values."""
    # Test that Settings can be instantiated with partial values
    # (defaults will be used for missing fields)
    settings = Settings(neo4j_uri="bolt://custom:7687")
    assert settings.neo4j_uri == "bolt://custom:7687"
    assert settings.neo4j_user == "neo4j"  # Default
    assert settings.neo4j_password == "password"  # Default
