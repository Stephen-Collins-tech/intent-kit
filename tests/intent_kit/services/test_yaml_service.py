"""
Tests for YAML service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from typing import Any

from intent_kit.services.yaml_service import YamlService, yaml_service


class TestYamlService:
    """Test YamlService class."""

    def test_init_with_yaml_available(self):
        """Test initialization when PyYAML is available."""
        with patch("intent_kit.services.yaml_service.yaml") as mock_yaml:
            service = YamlService()
            assert service.yaml == mock_yaml

    def test_init_without_yaml(self):
        """Test initialization when PyYAML is not available."""
        with patch("intent_kit.services.yaml_service.yaml", side_effect=ImportError):
            with patch("intent_kit.services.yaml_service.logger") as mock_logger:
                service = YamlService()
                assert service.yaml is None
                mock_logger.warning.assert_called_once()

    def test_safe_load_with_yaml_available(self):
        """Test safe_load when PyYAML is available."""
        with patch("intent_kit.services.yaml_service.yaml") as mock_yaml:
            mock_yaml.safe_load.return_value = {"key": "value"}
            service = YamlService()
            service.yaml = mock_yaml

            result = service.safe_load('{"key": "value"}')

            assert result == {"key": "value"}
            mock_yaml.safe_load.assert_called_once_with('{"key": "value"}')

    def test_safe_load_with_file_object(self):
        """Test safe_load with file-like object."""
        with patch("intent_kit.services.yaml_service.yaml") as mock_yaml:
            mock_yaml.safe_load.return_value = {"key": "value"}
            service = YamlService()
            service.yaml = mock_yaml

            file_obj = StringIO('{"key": "value"}')
            result = service.safe_load(file_obj)

            assert result == {"key": "value"}
            mock_yaml.safe_load.assert_called_once_with(file_obj)

    def test_safe_load_without_yaml(self):
        """Test safe_load when PyYAML is not available."""
        service = YamlService()
        service.yaml = None

        with pytest.raises(ImportError, match="PyYAML is required for YAML support"):
            service.safe_load("test")

    def test_dump_with_yaml_available(self):
        """Test dump when PyYAML is available."""
        with patch("intent_kit.services.yaml_service.yaml") as mock_yaml:
            mock_yaml.dump.return_value = "key: value\n"
            service = YamlService()
            service.yaml = mock_yaml

            data = {"key": "value"}
            result = service.dump(data)

            assert result == "key: value\n"
            mock_yaml.dump.assert_called_once_with(data, stream=None)

    def test_dump_with_stream(self):
        """Test dump with stream parameter."""
        with patch("intent_kit.services.yaml_service.yaml") as mock_yaml:
            mock_yaml.dump.return_value = None
            service = YamlService()
            service.yaml = mock_yaml

            data = {"key": "value"}
            stream = StringIO()
            result = service.dump(data, stream=stream)

            assert result is None
            mock_yaml.dump.assert_called_once_with(data, stream=stream)

    def test_dump_with_kwargs(self):
        """Test dump with additional keyword arguments."""
        with patch("intent_kit.services.yaml_service.yaml") as mock_yaml:
            mock_yaml.dump.return_value = "key: value\n"
            service = YamlService()
            service.yaml = mock_yaml

            data = {"key": "value"}
            result = service.dump(data, default_flow_style=False, indent=2)

            assert result == "key: value\n"
            mock_yaml.dump.assert_called_once_with(
                data, stream=None, default_flow_style=False, indent=2
            )

    def test_dump_without_yaml(self):
        """Test dump when PyYAML is not available."""
        service = YamlService()
        service.yaml = None

        with pytest.raises(ImportError, match="PyYAML is required for YAML support"):
            service.dump({"key": "value"})

    def test_dump_without_yaml_with_stream(self):
        """Test dump with stream when PyYAML is not available."""
        service = YamlService()
        service.yaml = None

        with pytest.raises(ImportError, match="PyYAML is required for YAML support"):
            service.dump({"key": "value"}, stream=StringIO())

    def test_safe_load_with_complex_data(self):
        """Test safe_load with complex YAML data."""
        with patch("intent_kit.services.yaml_service.yaml") as mock_yaml:
            complex_data = {
                "nested": {
                    "list": [1, 2, 3],
                    "dict": {"a": 1, "b": 2}
                },
                "array": ["item1", "item2"]
            }
            mock_yaml.safe_load.return_value = complex_data
            service = YamlService()
            service.yaml = mock_yaml

            yaml_string = """
            nested:
              list: [1, 2, 3]
              dict:
                a: 1
                b: 2
            array: [item1, item2]
            """
            result = service.safe_load(yaml_string)

            assert result == complex_data
            mock_yaml.safe_load.assert_called_once_with(yaml_string)

    def test_dump_with_complex_data(self):
        """Test dump with complex data structures."""
        with patch("intent_kit.services.yaml_service.yaml") as mock_yaml:
            mock_yaml.dump.return_value = "nested:\n  list: [1, 2, 3]\n"
            service = YamlService()
            service.yaml = mock_yaml

            complex_data = {
                "nested": {
                    "list": [1, 2, 3],
                    "dict": {"a": 1, "b": 2}
                },
                "array": ["item1", "item2"]
            }
            result = service.dump(complex_data)

            assert result == "nested:\n  list: [1, 2, 3]\n"
            mock_yaml.dump.assert_called_once_with(complex_data, stream=None)

    def test_safe_load_with_empty_string(self):
        """Test safe_load with empty string."""
        with patch("intent_kit.services.yaml_service.yaml") as mock_yaml:
            mock_yaml.safe_load.return_value = None
            service = YamlService()
            service.yaml = mock_yaml

            result = service.safe_load("")

            assert result is None
            mock_yaml.safe_load.assert_called_once_with("")

    def test_dump_with_empty_data(self):
        """Test dump with empty data."""
        with patch("intent_kit.services.yaml_service.yaml") as mock_yaml:
            mock_yaml.dump.return_value = "{}\n"
            service = YamlService()
            service.yaml = mock_yaml

            result = service.dump({})

            assert result == "{}\n"
            mock_yaml.dump.assert_called_once_with({}, stream=None)

    def test_safe_load_with_yaml_error(self):
        """Test safe_load when PyYAML raises an error."""
        with patch("intent_kit.services.yaml_service.yaml") as mock_yaml:
            mock_yaml.safe_load.side_effect = Exception("YAML parsing error")
            service = YamlService()
            service.yaml = mock_yaml

            with pytest.raises(Exception, match="YAML parsing error"):
                service.safe_load("invalid yaml")

    def test_dump_with_yaml_error(self):
        """Test dump when PyYAML raises an error."""
        with patch("intent_kit.services.yaml_service.yaml") as mock_yaml:
            mock_yaml.dump.side_effect = Exception("YAML dumping error")
            service = YamlService()
            service.yaml = mock_yaml

            with pytest.raises(Exception, match="YAML dumping error"):
                service.dump({"key": "value"})


class TestYamlServiceSingleton:
    """Test the singleton yaml_service instance."""

    def test_singleton_instance(self):
        """Test that yaml_service is a singleton instance."""
        assert isinstance(yaml_service, YamlService)

    @patch("intent_kit.services.yaml_service.yaml")
    def test_singleton_safe_load(self, mock_yaml):
        """Test safe_load on singleton instance."""
        mock_yaml.safe_load.return_value = {"key": "value"}
        
        result = yaml_service.safe_load('{"key": "value"}')
        
        assert result == {"key": "value"}
        mock_yaml.safe_load.assert_called_once_with('{"key": "value"}')

    @patch("intent_kit.services.yaml_service.yaml")
    def test_singleton_dump(self, mock_yaml):
        """Test dump on singleton instance."""
        mock_yaml.dump.return_value = "key: value\n"
        
        result = yaml_service.dump({"key": "value"})
        
        assert result == "key: value\n"
        mock_yaml.dump.assert_called_once_with({"key": "value"}, stream=None)

    def test_singleton_without_yaml(self):
        """Test singleton when PyYAML is not available."""
        # Temporarily set yaml to None
        original_yaml = yaml_service.yaml
        yaml_service.yaml = None
        
        try:
            with pytest.raises(ImportError, match="PyYAML is required for YAML support"):
                yaml_service.safe_load("test")
            
            with pytest.raises(ImportError, match="PyYAML is required for YAML support"):
                yaml_service.dump({"key": "value"})
        finally:
            yaml_service.yaml = original_yaml


class TestYamlServiceIntegration:
    """Integration tests for YamlService."""

    def test_full_workflow_with_yaml_available(self):
        """Test complete workflow when PyYAML is available."""
        with patch("intent_kit.services.yaml_service.yaml") as mock_yaml:
            # Mock the YAML module
            mock_yaml.safe_load.return_value = {"input": "data"}
            mock_yaml.dump.return_value = "input: data\n"
            
            service = YamlService()
            service.yaml = mock_yaml
            
            # Test loading
            loaded_data = service.safe_load("input: data")
            assert loaded_data == {"input": "data"}
            
            # Test dumping
            dumped_data = service.dump(loaded_data)
            assert dumped_data == "input: data\n"
            
            # Verify calls
            mock_yaml.safe_load.assert_called_once_with("input: data")
            mock_yaml.dump.assert_called_once_with({"input": "data"}, stream=None)

    def test_full_workflow_without_yaml(self):
        """Test complete workflow when PyYAML is not available."""
        with patch("intent_kit.services.yaml_service.yaml", side_effect=ImportError):
            with patch("intent_kit.services.yaml_service.logger") as mock_logger:
                service = YamlService()
                
                # Should not be able to load
                with pytest.raises(ImportError, match="PyYAML is required for YAML support"):
                    service.safe_load("test")
                
                # Should not be able to dump
                with pytest.raises(ImportError, match="PyYAML is required for YAML support"):
                    service.dump({"key": "value"})
                
                # Should have logged warning
                mock_logger.warning.assert_called_once()

    def test_file_like_object_handling(self):
        """Test handling of file-like objects."""
        with patch("intent_kit.services.yaml_service.yaml") as mock_yaml:
            mock_yaml.safe_load.return_value = {"from_file": "data"}
            mock_yaml.dump.return_value = "from_file: data\n"
            
            service = YamlService()
            service.yaml = mock_yaml
            
            # Test with StringIO
            file_obj = StringIO("from_file: data")
            loaded_data = service.safe_load(file_obj)
            assert loaded_data == {"from_file": "data"}
            
            # Test dumping to file
            output_file = StringIO()
            service.dump(loaded_data, stream=output_file)
            mock_yaml.dump.assert_called_with({"from_file": "data"}, stream=output_file)

    def test_error_propagation(self):
        """Test that errors from PyYAML are properly propagated."""
        with patch("intent_kit.services.yaml_service.yaml") as mock_yaml:
            mock_yaml.safe_load.side_effect = ValueError("Invalid YAML")
            mock_yaml.dump.side_effect = TypeError("Cannot serialize")
            
            service = YamlService()
            service.yaml = mock_yaml
            
            # Test safe_load error
            with pytest.raises(ValueError, match="Invalid YAML"):
                service.safe_load("invalid")
            
            # Test dump error
            with pytest.raises(TypeError, match="Cannot serialize"):
                service.dump({"key": "value"})