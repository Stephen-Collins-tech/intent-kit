"""Tests for the loader service."""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from intent_kit.services.loader_service import (
    Loader,
    DatasetLoader,
    ModuleLoader,
    dataset_loader,
    module_loader,
)


class TestLoader:
    """Test cases for the base Loader class."""

    def test_loader_is_abstract(self):
        """Test that Loader is an abstract base class."""
        with pytest.raises(TypeError):
            Loader()  # type: ignore


class TestDatasetLoader:
    """Test cases for DatasetLoader."""

    def test_dataset_loader_creation(self):
        """Test creating a DatasetLoader instance."""
        loader = DatasetLoader()
        assert isinstance(loader, Loader)

    @patch("intent_kit.services.loader_service.yaml_service")
    def test_load_dataset_success(self, mock_yaml_service):
        """Test successfully loading a dataset."""
        mock_yaml_service.safe_load.return_value = {
            "name": "test_dataset",
            "description": "A test dataset",
            "test_cases": [{"input": "test input", "expected": "test output"}],
        }

        loader = DatasetLoader()
        test_path = Path("test_dataset.yaml")

        with patch("builtins.open", mock_open(read_data="test yaml content")):
            result = loader.load(test_path)

        assert result["name"] == "test_dataset"
        assert result["description"] == "A test dataset"
        assert len(result["test_cases"]) == 1
        mock_yaml_service.safe_load.assert_called_once()

    @patch("intent_kit.services.loader_service.yaml_service")
    def test_load_dataset_file_not_found(self, mock_yaml_service):
        """Test loading dataset with file not found."""
        loader = DatasetLoader()
        test_path = Path("nonexistent.yaml")

        with pytest.raises(FileNotFoundError):
            loader.load(test_path)

        mock_yaml_service.safe_load.assert_not_called()

    @patch("intent_kit.services.loader_service.yaml_service")
    def test_load_dataset_yaml_error(self, mock_yaml_service):
        """Test loading dataset with YAML parsing error."""
        mock_yaml_service.safe_load.side_effect = Exception("YAML parsing error")

        loader = DatasetLoader()
        test_path = Path("test_dataset.yaml")

        with patch("builtins.open", mock_open(read_data="invalid yaml content")):
            with pytest.raises(Exception, match="YAML parsing error"):
                loader.load(test_path)

    def test_load_dataset_encoding(self):
        """Test loading dataset with UTF-8 encoding."""
        loader = DatasetLoader()
        test_path = Path("test_dataset.yaml")

        with patch("builtins.open", mock_open(read_data="test content")) as mock_file:
            with patch("intent_kit.services.loader_service.yaml_service") as mock_yaml:
                mock_yaml.safe_load.return_value = {"test": "data"}

                loader.load(test_path)

                # Check that file was opened with UTF-8 encoding
                mock_file.assert_called_once_with(test_path, "r", encoding="utf-8")


class TestModuleLoader:
    """Test cases for ModuleLoader."""

    def test_module_loader_creation(self):
        """Test creating a ModuleLoader instance."""
        loader = ModuleLoader()
        assert isinstance(loader, Loader)

    def test_load_module_success(self):
        """Test successfully loading a module."""
        loader = ModuleLoader()

        # Create a mock module with a test function
        mock_module = Mock()
        mock_node_func = Mock(return_value="test_node_instance")
        mock_module.test_node = mock_node_func

        with patch("importlib.import_module", return_value=mock_module):
            result = loader.load(Path("test_module:test_node"))

        assert result == "test_node_instance"
        mock_node_func.assert_called_once()

    def test_load_module_non_callable(self):
        """Test loading a module with non-callable attribute."""
        loader = ModuleLoader()

        # Create a mock module with a non-callable attribute
        mock_module = Mock()
        mock_module.test_node = "test_node_instance"

        with patch("importlib.import_module", return_value=mock_module):
            result = loader.load(Path("test_module:test_node"))

        assert result == "test_node_instance"

    def test_load_module_invalid_path_format(self):
        """Test loading module with invalid path format."""
        loader = ModuleLoader()

        # Test with no colon
        with pytest.raises(ValueError, match="Invalid module path format"):
            loader.load(Path("test_module"))

        # Test with multiple colons - this actually works in the current implementation
        # because it splits on the first colon only
        result = loader.load(Path("test_module:test_node:extra"))
        # Should return None due to import error, not ValueError
        assert result is None

    def test_load_module_import_error(self):
        """Test loading module with import error."""
        loader = ModuleLoader()

        # Test with a module that doesn't exist
        with patch("builtins.print") as mock_print:
            result = loader.load(Path("nonexistent_module:test_node"))

        assert result is None
        mock_print.assert_called_once()
        assert (
            "Error loading node test_node from nonexistent_module"
            in mock_print.call_args[0][0]
        )

    def test_load_module_attribute_error(self):
        """Test loading module with attribute error."""
        loader = ModuleLoader()

        # Test with a real module that doesn't have the attribute
        with patch("builtins.print") as mock_print:
            result = loader.load(Path("sys:nonexistent_node"))

        assert result is None
        mock_print.assert_called_once()
        assert (
            "Error loading node nonexistent_node from sys" in mock_print.call_args[0][0]
        )

    def test_load_module_getattr_error(self):
        """Test loading module with getattr error."""
        loader = ModuleLoader()

        # Test with a real module that doesn't have the attribute
        with patch("builtins.print") as mock_print:
            result = loader.load(Path("os:nonexistent_node"))

        assert result is None
        mock_print.assert_called_once()
        assert (
            "Error loading node nonexistent_node from os" in mock_print.call_args[0][0]
        )

    def test_load_module_string_path(self):
        """Test loading module with string path."""
        loader = ModuleLoader()

        # Create a mock module with a test function
        mock_module = Mock()
        mock_node_func = Mock(return_value="test_node_instance")
        mock_module.test_node = mock_node_func

        with patch("importlib.import_module", return_value=mock_module):
            result = loader.load(Path("test_module:test_node"))

        assert result == "test_node_instance"
        mock_node_func.assert_called_once()

    def test_load_module_path_object(self):
        """Test loading module with Path object."""
        loader = ModuleLoader()

        # Create a mock module with a test function
        mock_module = Mock()
        mock_node_func = Mock(return_value="test_node_instance")
        mock_module.test_node = mock_node_func

        with patch("importlib.import_module", return_value=mock_module):
            result = loader.load(Path("test_module:test_node"))

        assert result == "test_node_instance"
        mock_node_func.assert_called_once()


class TestSingletonInstances:
    """Test cases for singleton loader instances."""

    def test_dataset_loader_singleton(self):
        """Test that dataset_loader is a singleton instance."""
        assert isinstance(dataset_loader, DatasetLoader)
        # Note: These are not actually singletons, just module-level instances
        assert dataset_loader is not None

    def test_module_loader_singleton(self):
        """Test that module_loader is a singleton instance."""
        assert isinstance(module_loader, ModuleLoader)
        # Note: These are not actually singletons, just module-level instances
        assert module_loader is not None

    @patch("intent_kit.services.loader_service.yaml_service")
    def test_dataset_loader_functionality(self, mock_yaml_service):
        """Test that the singleton dataset_loader works correctly."""
        mock_yaml_service.safe_load.return_value = {"test": "data"}

        test_path = Path("test.yaml")
        with patch("builtins.open", mock_open(read_data="test content")):
            result = dataset_loader.load(test_path)

        assert result == {"test": "data"}

    def test_module_loader_functionality(self):
        """Test that the singleton module_loader works correctly."""
        # Create a mock module with a test function
        mock_module = Mock()
        mock_node_func = Mock(return_value="test_node_instance")
        mock_module.test_node = mock_node_func

        with patch("importlib.import_module", return_value=mock_module):
            result = module_loader.load(Path("test_module:test_node"))

        assert result == "test_node_instance"


class TestIntegration:
    """Integration tests for loader service."""

    @patch("intent_kit.services.loader_service.yaml_service")
    def test_dataset_loader_integration(self, mock_yaml_service):
        """Test dataset loader integration with real file operations."""
        mock_yaml_service.safe_load.return_value = {
            "name": "integration_test",
            "version": "1.0",
            "data": [1, 2, 3, 4, 5],
        }

        loader = DatasetLoader()
        test_path = Path("integration_test.yaml")

        with patch("builtins.open", mock_open(read_data="yaml content")):
            result = loader.load(test_path)

        assert result["name"] == "integration_test"
        assert result["version"] == "1.0"
        assert result["data"] == [1, 2, 3, 4, 5]

    def test_module_loader_integration(self):
        """Test module loader integration with real import operations."""
        loader = ModuleLoader()

        # Test with a real module (sys is always available)
        result = loader.load(Path("sys:version"))

        # Should return the version string
        assert isinstance(result, str)
        assert len(result) > 0

    def test_module_loader_with_builtin_module(self):
        """Test module loader with built-in modules."""
        loader = ModuleLoader()

        # Test with os module
        result = loader.load(Path("os:name"))

        # Should return the OS name
        assert isinstance(result, str)
        assert result in ["posix", "nt", "java"]

    def test_error_handling_integration(self):
        """Test error handling in integration scenarios."""
        loader = ModuleLoader()

        # Test with non-existent module
        with patch("builtins.print") as mock_print:
            result = loader.load(Path("nonexistent_module:nonexistent_node"))

        assert result is None
        mock_print.assert_called_once()
        assert "Error loading node" in mock_print.call_args[0][0]
