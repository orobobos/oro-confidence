"""Shared test fixtures for our-confidence."""

import pytest

from our_confidence.dimension_registry import reset_registry


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "unit: Unit tests (no external dependencies)")
    config.addinivalue_line("markers", "integration: Integration tests (require external services)")
    config.addinivalue_line("markers", "slow: Slow tests (>5s)")


@pytest.fixture(autouse=True)
def _reset_registry() -> None:
    """Reset the dimension registry before each test to ensure isolation."""
    reset_registry()
