"""Tests for the Quasar component verifier."""

import json
import pytest
from pathlib import Path
from unittest.mock import mock_open, patch

from nicegui_atlas.quasar_verifier import (
    get_web_types,
    extract_quasar_props,
    compare_props,
    verify_component,
    verify_components
)


@pytest.fixture
def mock_web_types():
    """Create mock web-types data."""
    return {
        "contributions": {
            "html": {
                "types-syntax": [
                    {
                        "name": "QBtn",
                        "source": {"module": "quasar"},
                        "symbol": "Btn",
                        "properties": [
                            {
                                "name": "color",
                                "type": "string",
                                "description": "Color name for component"
                            }
                        ]
                    }
                ],
                "tags": [
                    {
                        "name": "q-btn",
                        "attributes": [
                            {
                                "name": "size",
                                "type": "string",
                                "description": "Size of the component"
                            }
                        ]
                    }
                ]
            }
        }
    }


def test_get_web_types(tmp_path):
    """Test loading web-types from file."""
    # Create mock web-types file
    web_types_file = tmp_path / "quasar-web-types.json"
    web_types_data = {"test": "data"}
    web_types_file.write_text(json.dumps(web_types_data))
    
    # Mock the file path
    with patch('nicegui_atlas.quasar_verifier.WEB_TYPES_FILE', web_types_file):
        result = get_web_types()
        assert result == web_types_data


def test_get_web_types_file_not_found():
    """Test error handling when web-types file is not found."""
    with patch('nicegui_atlas.quasar_verifier.WEB_TYPES_FILE', Path('/nonexistent/file.json')):
        with pytest.raises(Exception) as exc_info:
            get_web_types()
        assert "Failed to load web-types.json" in str(exc_info.value)


def test_extract_quasar_props(mock_web_types):
    """Test extracting properties from web-types."""
    props = extract_quasar_props("QBtn", mock_web_types)
    assert "color" in props
    assert "size" in props
    assert props["color"] == "Color name for component"
    assert props["size"] == "Size of the component"


def test_compare_props():
    """Test comparing properties."""
    quasar_props = {
        "color": "Color name",
        "size": "Size value"
    }
    our_props = {
        "color": "Our color",
        "extra": "Extra prop"
    }
    
    missing, extra = compare_props(quasar_props, our_props)
    assert missing == {"size"}
    assert extra == {"extra"}


def test_verify_component(mock_web_types):
    """Test verifying a single component."""
    component_data = {
        "quasar_props": {
            "color": "Color prop",
            "extra": "Extra prop"
        }
    }
    
    with patch('nicegui_atlas.quasar_verifier.load_config', return_value={"quasar_version": "2.0.0"}):
        issues = verify_component("QBtn", "https://quasar.dev/vue-components/button", component_data, mock_web_types)
    
    assert len(issues) == 2
    assert any("Missing Quasar properties: size" in issue for issue in issues)
    assert any("Extra properties not in Quasar docs: extra" in issue for issue in issues)


def test_verify_components(tmp_path, mock_web_types):
    """Test verifying multiple components."""
    # Create mock component file
    component_file = tmp_path / "button.json"
    component_data = {
        "quasar_components": ["QBtn"],
        "quasar_props": {
            "color": "Color prop"
        }
    }
    component_file.write_text(json.dumps(component_data))
    
    # Mock web-types loading
    with patch('nicegui_atlas.quasar_verifier.get_web_types', return_value=mock_web_types):
        with patch('nicegui_atlas.quasar_verifier.load_config', return_value={"quasar_version": "2.0.0"}):
            results = verify_components([str(component_file)])
    
    assert "button.json" in results
    assert len(results["button.json"]) == 1
    assert "Missing Quasar properties: size" in results["button.json"][0]
