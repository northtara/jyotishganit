"""
Test cross-platform data directory functionality.
"""
import os
import platform
import tempfile
import pytest
from unittest.mock import patch
from pathlib import Path

def test_data_directory_platform_specific():
    """Test that data directory follows platform conventions."""
    # Import here to avoid issues with missing dependencies in CI
    try:
        from jyotishganit.core.astronomical import _get_data_directory
    except ImportError:
        pytest.skip("Skyfield not available for testing")
    
    # Test each platform
    test_cases = [
        ("Windows", {"LOCALAPPDATA": "C:\\Users\\test\\AppData\\Local"}, 
         os.path.join("C:\\Users\\test\\AppData\\Local", "jyotishganit")),
        ("Darwin", {}, os.path.expanduser("~/Library/Application Support/jyotishganit")),
        ("Linux", {}, os.path.expanduser("~/.local/share/jyotishganit")),
        ("Linux", {"XDG_DATA_HOME": "/custom/data"}, os.path.join("/custom/data", "jyotishganit")),
    ]
    
    for system, env_vars, expected in test_cases:
        with patch('platform.system', return_value=system):
            with patch.dict(os.environ, env_vars, clear=False):
                result = _get_data_directory()
                # Normalize paths for comparison
                result_normalized = os.path.normpath(result)
                expected_normalized = os.path.normpath(expected)
                assert result_normalized == expected_normalized, f"Platform {system}: got {result}, expected {expected}"

def test_data_directory_creation():
    """Test that data directory can be created."""
    try:
        from jyotishganit.core.astronomical import _get_data_directory
    except ImportError:
        pytest.skip("Skyfield not available for testing")
    
    # Simply test that the function returns a valid path string
    data_dir = _get_data_directory()
    
    assert isinstance(data_dir, str), "Data directory path should be a string"
    assert len(data_dir) > 0, "Data directory path should not be empty"
    assert "jyotishganit" in data_dir, "Data directory should contain 'jyotishganit' in path"

def test_cross_platform_path_handling():
    """Test that paths work correctly across platforms."""
    try:
        from jyotishganit.core.astronomical import _get_data_directory
    except ImportError:
        pytest.skip("Skyfield not available for testing")
    
    data_dir = _get_data_directory()
    
    # Should be an absolute path
    assert os.path.isabs(data_dir), f"Data directory should be absolute: {data_dir}"
    
    # Should not contain invalid characters for any platform  
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in invalid_chars:
        assert char not in os.path.basename(data_dir), f"Invalid character {char} in directory name"
    
    # Should be writable (test with parent directory)
    parent_dir = os.path.dirname(data_dir)
    if os.path.exists(parent_dir):
        assert os.access(parent_dir, os.W_OK), f"Parent directory should be writable: {parent_dir}"

if __name__ == "__main__":
    # Run tests directly
    test_data_directory_platform_specific()
    test_cross_platform_path_handling()
    print("✅ All cross-platform tests passed!")