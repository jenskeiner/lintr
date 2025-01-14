"""Shared test fixtures for repolint."""

import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Any, Generator

import pytest
import yaml

from repolint.config import RepolintConfig


@pytest.fixture
def mock_config() -> Generator[Path, None, None]:
    """Create a temporary configuration file with the given configuration.
    
    This fixture creates a temporary YAML file with the provided configuration and
    yields its path. The file is automatically cleaned up after the test.
    
    Example:
        def test_with_custom_config(mock_config):
            config = {
                "github": {"token": "test-token"},
                "repository_filter": {
                    "include_patterns": ["test-*"],
                    "exclude_patterns": ["test-excluded"]
                },
                "rule_sets": [
                    {
                        "name": "test-ruleset",
                        "rules": ["R001", "R002"]
                    }
                ]
            }
            config_path = mock_config(config)
            # Use config_path in your test...
    """
    temp_file = NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    try:
        def _create_config(config: Dict[str, Any]) -> Path:
            yaml.safe_dump(config, temp_file)
            temp_file.flush()
            return Path(temp_file.name)
        
        yield _create_config
    finally:
        temp_file.close()
        os.unlink(temp_file.name)


@pytest.fixture
def mock_config_file(mock_config) -> Generator[Path, None, None]:
    """Create a temporary configuration file with default test configuration.
    
    This fixture provides a ready-to-use configuration file with sensible defaults
    for testing. Use this when you don't need to customize the configuration.
    """
    default_config = {
        "github": {
            "token": "test-token"
        },
        "repository_filter": {
            "include_patterns": ["test-*"],
            "exclude_patterns": []
        },
        "rule_sets": [
            {
                "name": "default",
                "rules": ["R001"]
            }
        ]
    }
    yield mock_config(default_config)
