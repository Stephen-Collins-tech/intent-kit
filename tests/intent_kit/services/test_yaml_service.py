"""
Tests for YAML service.
"""

import pytest
import os
from unittest.mock import patch, Mock
from io import StringIO

from intent_kit.services.yaml_service import YamlService, yaml_service


class TestYamlService:
    """Test YamlService class."""

    def test_init_with_yaml_available(self):
        """Test initialization when PyYAML is available."""
        service = YamlService()
        assert service.yaml is not None

    def test_init_without_yaml(self):
        """Test initialization when PyYAML is not available."""
        with patch(
            "builtins.__import__", side_effect=ImportError("No module named 'yaml'")
        ):
            with patch("intent_kit.services.yaml_service.logger") as mock_logger:
                service = YamlService()
                assert service.yaml is None
                mock_logger.warning.assert_called_once()

    def test_safe_load_with_yaml_available(self):
        """Test safe_load when PyYAML is available."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.safe_load.return_value = {"key": "value"}
        service.yaml = mock_yaml

        result = service.safe_load('{"key": "value"}')

        assert result == {"key": "value"}
        mock_yaml.safe_load.assert_called_once_with('{"key": "value"}')

    def test_safe_load_with_file_object(self):
        """Test safe_load with file-like object."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.safe_load.return_value = {"key": "value"}
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
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.dump.return_value = "key: value\n"
        service.yaml = mock_yaml

        data = {"key": "value"}
        result = service.dump(data)

        assert result == "key: value\n"
        mock_yaml.dump.assert_called_once_with(data, stream=None)

    def test_dump_with_stream(self):
        """Test dump with stream parameter."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.dump.return_value = None
        service.yaml = mock_yaml

        data = {"key": "value"}
        stream = StringIO()
        result = service.dump(data, stream=stream)

        assert result is None
        mock_yaml.dump.assert_called_once_with(data, stream=stream)

    def test_dump_with_kwargs(self):
        """Test dump with additional keyword arguments."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.dump.return_value = "key: value\n"
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
        service = YamlService()
        mock_yaml = Mock()
        complex_data = {
            "nested": {"list": [1, 2, 3], "dict": {"a": 1, "b": 2}},
            "array": ["item1", "item2"],
        }
        mock_yaml.safe_load.return_value = complex_data
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
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.dump.return_value = "nested:\n  list: [1, 2, 3]\n"
        service.yaml = mock_yaml

        complex_data = {
            "nested": {"list": [1, 2, 3], "dict": {"a": 1, "b": 2}},
            "array": ["item1", "item2"],
        }
        result = service.dump(complex_data)

        assert result == "nested:\n  list: [1, 2, 3]\n"
        mock_yaml.dump.assert_called_once_with(complex_data, stream=None)

    def test_safe_load_with_empty_string(self):
        """Test safe_load with empty string."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.safe_load.return_value = None
        service.yaml = mock_yaml

        result = service.safe_load("")

        assert result is None
        mock_yaml.safe_load.assert_called_once_with("")

    def test_dump_with_empty_data(self):
        """Test dump with empty data."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.dump.return_value = "{}\n"
        service.yaml = mock_yaml

        result = service.dump({})

        assert result == "{}\n"
        mock_yaml.dump.assert_called_once_with({}, stream=None)

    def test_safe_load_with_yaml_error(self):
        """Test safe_load when PyYAML raises an error."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.safe_load.side_effect = Exception("YAML parsing error")
        service.yaml = mock_yaml

        with pytest.raises(Exception, match="YAML parsing error"):
            service.safe_load("invalid yaml")

    def test_dump_with_yaml_error(self):
        """Test dump when PyYAML raises an error."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.dump.side_effect = Exception("YAML dumping error")
        service.yaml = mock_yaml

        with pytest.raises(Exception, match="YAML dumping error"):
            service.dump({"key": "value"})

    def test_safe_load_with_none_input(self):
        """Test safe_load with None input."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.safe_load.return_value = None
        service.yaml = mock_yaml

        result = service.safe_load(None)

        assert result is None
        mock_yaml.safe_load.assert_called_once_with(None)

    def test_dump_with_none_input(self):
        """Test dump with None input."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.dump.return_value = "null\n"
        service.yaml = mock_yaml

        result = service.dump(None)

        assert result == "null\n"
        mock_yaml.dump.assert_called_once_with(None, stream=None)

    def test_safe_load_with_unicode_string(self):
        """Test safe_load with unicode string."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.safe_load.return_value = {"unicode": "测试"}
        service.yaml = mock_yaml

        yaml_string = "unicode: 测试"
        result = service.safe_load(yaml_string)

        assert result == {"unicode": "测试"}
        mock_yaml.safe_load.assert_called_once_with(yaml_string)

    def test_dump_with_unicode_data(self):
        """Test dump with unicode data."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.dump.return_value = "unicode: 测试\n"
        service.yaml = mock_yaml

        data = {"unicode": "测试"}
        result = service.dump(data)

        assert result == "unicode: 测试\n"
        mock_yaml.dump.assert_called_once_with(data, stream=None)

    def test_safe_load_with_binary_data(self):
        """Test safe_load with binary data."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.safe_load.return_value = {"binary": b"data"}
        service.yaml = mock_yaml

        binary_data = b"binary: data"
        result = service.safe_load(binary_data)

        assert result == {"binary": b"data"}
        mock_yaml.safe_load.assert_called_once_with(binary_data)

    def test_dump_with_binary_data(self):
        """Test dump with binary data."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.dump.return_value = b"binary: data\n"
        service.yaml = mock_yaml

        data = {"binary": b"data"}
        result = service.dump(data)

        assert result == b"binary: data\n"
        mock_yaml.dump.assert_called_once_with(data, stream=None)

    def test_safe_load_with_custom_loader(self):
        """Test safe_load with custom loader."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.safe_load.return_value = {"custom": "loader"}
        service.yaml = mock_yaml

        result = service.safe_load("custom: loader")

        assert result == {"custom": "loader"}
        mock_yaml.safe_load.assert_called_once_with("custom: loader")

    def test_dump_with_custom_dumper(self):
        """Test dump with custom dumper."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.dump.return_value = "custom: dumper\n"
        service.yaml = mock_yaml

        data = {"custom": "dumper"}
        result = service.dump(data)

        assert result == "custom: dumper\n"
        mock_yaml.dump.assert_called_once_with(data, stream=None)

    def test_environment_variable_integration(self):
        """Test that YAML service can work with environment variables."""
        # This test verifies that the YAML service can be used
        # in conjunction with environment-based configurations
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.safe_load.return_value = {"env_key": "env_value"}
        service.yaml = mock_yaml

        # Test loading YAML that might contain environment variables
        result = service.safe_load("env_key: env_value")
        assert result == {"env_key": "env_value"}

    def test_error_handling_with_invalid_yaml(self):
        """Test error handling with invalid YAML data."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.safe_load.side_effect = Exception("Invalid YAML")
        service.yaml = mock_yaml

        with pytest.raises(Exception, match="Invalid YAML"):
            service.safe_load("invalid: yaml: data")

    def test_error_handling_with_invalid_data_types(self):
        """Test error handling with invalid data types for dumping."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.dump.side_effect = Exception("Invalid data type")
        service.yaml = mock_yaml

        with pytest.raises(Exception, match="Invalid data type"):
            service.dump({"key": object()})  # Non-serializable object


class TestYamlServiceSingleton:
    """Test YamlService singleton functionality."""

    def test_singleton_instance(self):
        """Test that yaml_service is a singleton instance."""
        assert yaml_service is not None
        assert isinstance(yaml_service, YamlService)

    def test_singleton_safe_load(self):
        """Test singleton safe_load method."""
        mock_yaml = Mock()
        mock_yaml.safe_load.return_value = {"singleton": "test"}
        yaml_service.yaml = mock_yaml

        result = yaml_service.safe_load('{"singleton": "test"}')

        assert result == {"singleton": "test"}
        mock_yaml.safe_load.assert_called_once_with('{"singleton": "test"}')

    def test_singleton_dump(self):
        """Test singleton dump method."""
        mock_yaml = Mock()
        mock_yaml.dump.return_value = "singleton: test\n"
        yaml_service.yaml = mock_yaml

        data = {"singleton": "test"}
        result = yaml_service.dump(data)

        assert result == "singleton: test\n"
        mock_yaml.dump.assert_called_once_with(data, stream=None)

    def test_singleton_without_yaml(self):
        """Test singleton when PyYAML is not available."""
        original_yaml = yaml_service.yaml
        yaml_service.yaml = None

        try:
            with pytest.raises(
                ImportError, match="PyYAML is required for YAML support"
            ):
                yaml_service.safe_load("test")

            with pytest.raises(
                ImportError, match="PyYAML is required for YAML support"
            ):
                yaml_service.dump({"key": "value"})
        finally:
            yaml_service.yaml = original_yaml


class TestYamlServiceIntegration:
    """Test YamlService integration scenarios."""

    def test_full_workflow_with_yaml_available(self):
        """Test complete YAML workflow when PyYAML is available."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.safe_load.return_value = {"input": "data"}
        mock_yaml.dump.return_value = "input: data\n"
        service.yaml = mock_yaml

        # Load YAML
        loaded_data = service.safe_load("input: data")
        assert loaded_data == {"input": "data"}

        # Dump YAML
        dumped_data = service.dump(loaded_data)
        assert dumped_data == "input: data\n"

        # Verify calls
        mock_yaml.safe_load.assert_called_once_with("input: data")
        mock_yaml.dump.assert_called_once_with({"input": "data"}, stream=None)

    def test_full_workflow_without_yaml(self):
        """Test complete YAML workflow when PyYAML is not available."""
        service = YamlService()
        service.yaml = None

        # Both operations should fail
        with pytest.raises(ImportError, match="PyYAML is required for YAML support"):
            service.safe_load("input: data")

        with pytest.raises(ImportError, match="PyYAML is required for YAML support"):
            service.dump({"input": "data"})

    def test_file_like_object_handling(self):
        """Test handling of file-like objects."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.safe_load.return_value = {"file": "content"}
        mock_yaml.dump.return_value = "file: content\n"
        service.yaml = mock_yaml

        # Test with StringIO
        input_file = StringIO("file: content")
        loaded_data = service.safe_load(input_file)
        assert loaded_data == {"file": "content"}

        # Test with output file
        output_file = StringIO()
        service.dump({"file": "content"}, stream=output_file)
        # The dump method should write to the stream, not return a value
        assert output_file.getvalue() == ""
        # The mock should have been called with the stream
        mock_yaml.dump.assert_called_with({"file": "content"}, stream=output_file)

    def test_error_propagation(self):
        """Test that errors are properly propagated."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.safe_load.side_effect = ValueError("Invalid YAML")
        mock_yaml.dump.side_effect = TypeError("Invalid data type")
        service.yaml = mock_yaml

        # Test safe_load error
        with pytest.raises(ValueError, match="Invalid YAML"):
            service.safe_load("invalid yaml")

        # Test dump error
        with pytest.raises(TypeError, match="Invalid data type"):
            service.dump({"key": "value"})

    def test_llm_config_integration(self):
        """Test YAML service integration with LLM configurations."""
        service = YamlService()
        mock_yaml = Mock()

        # Mock LLM configuration data
        llm_config = {
            "provider": "openai",
            "api_key": "test-key",
            "model": "gpt-4",
            "max_tokens": 1000,
        }
        mock_yaml.safe_load.return_value = llm_config
        service.yaml = mock_yaml

        # Test loading LLM config from YAML
        result = service.safe_load("provider: openai\napi_key: test-key")
        assert result == llm_config
        assert result["provider"] == "openai"
        assert result["api_key"] == "test-key"

    @patch.dict(os.environ, {"YAML_CONFIG_PATH": "/tmp/config.yaml"})
    def test_environment_variable_support(self):
        """Test that YAML service can work with environment variables."""
        service = YamlService()
        mock_yaml = Mock()
        mock_yaml.safe_load.return_value = {"env_config": "value"}
        service.yaml = mock_yaml

        # Test loading YAML that might reference environment variables
        result = service.safe_load("env_config: value")
        assert result == {"env_config": "value"}
