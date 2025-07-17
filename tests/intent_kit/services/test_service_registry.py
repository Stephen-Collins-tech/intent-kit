"""
Tests for service registry.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Type, Any

from intent_kit.services import (
    ServiceRegistry,
    get_available_services,
    create_service,
)


class TestServiceRegistry:
    """Test ServiceRegistry class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Reset the registry for each test
        ServiceRegistry._services = {
            "google": Mock(),
            "anthropic": Mock(),
            "openai": Mock(),
            "ollama": Mock(),
        }

    def test_get_available_services_all_available(self):
        """Test getting available services when all are available."""
        # Mock all services as available
        for service_class in ServiceRegistry._services.values():
            service_class.is_available = Mock(return_value=True)

        result = ServiceRegistry.get_available_services()

        expected = {
            "google": True,
            "anthropic": True,
            "openai": True,
            "ollama": True,
        }
        assert result == expected

    def test_get_available_services_some_unavailable(self):
        """Test getting available services when some are unavailable."""
        # Mock some services as unavailable
        ServiceRegistry._services["google"].is_available = Mock(return_value=False)
        ServiceRegistry._services["anthropic"].is_available = Mock(return_value=True)
        ServiceRegistry._services["openai"].is_available = Mock(return_value=False)
        ServiceRegistry._services["ollama"].is_available = Mock(return_value=True)

        result = ServiceRegistry.get_available_services()

        expected = {
            "google": False,
            "anthropic": True,
            "openai": False,
            "ollama": True,
        }
        assert result == expected

    def test_get_available_services_no_check_method(self):
        """Test getting available services when service has no is_available method."""
        # Remove is_available method from one service
        del ServiceRegistry._services["google"].is_available

        result = ServiceRegistry.get_available_services()

        # Should assume available if no check method
        assert result["google"] is True

    def test_create_service_success(self):
        """Test creating a service successfully."""
        mock_service = Mock()
        ServiceRegistry._services["test"] = Mock(return_value=mock_service)

        result = ServiceRegistry.create_service("test", api_key="test_key")

        assert result == mock_service
        ServiceRegistry._services["test"].assert_called_once_with(api_key="test_key")

    def test_create_service_unknown_service(self):
        """Test creating an unknown service raises ValueError."""
        with pytest.raises(ValueError, match="Unknown service: unknown"):
            ServiceRegistry.create_service("unknown")

    def test_create_service_unavailable(self):
        """Test creating an unavailable service raises ImportError."""
        mock_service_class = Mock()
        mock_service_class.is_available = Mock(return_value=False)
        ServiceRegistry._services["unavailable"] = mock_service_class

        with pytest.raises(ImportError, match="Service 'unavailable' is not available"):
            ServiceRegistry.create_service("unavailable")

    def test_create_service_unavailable_no_check_method(self):
        """Test creating service when is_available method doesn't exist."""
        mock_service_class = Mock()
        # Remove is_available method
        if hasattr(mock_service_class, "is_available"):
            del mock_service_class.is_available
        ServiceRegistry._services["test"] = mock_service_class

        # Should not raise error since no is_available method
        result = ServiceRegistry.create_service("test")
        assert result is not None

    def test_register_service(self):
        """Test registering a new service."""
        mock_service_class = Mock()
        
        ServiceRegistry.register_service("new_service", mock_service_class)
        
        assert ServiceRegistry._services["new_service"] == mock_service_class

    def test_register_service_overwrite(self):
        """Test registering a service overwrites existing one."""
        old_service = Mock()
        new_service = Mock()
        ServiceRegistry._services["existing"] = old_service
        
        ServiceRegistry.register_service("existing", new_service)
        
        assert ServiceRegistry._services["existing"] == new_service

    def test_create_service_with_kwargs(self):
        """Test creating service with various keyword arguments."""
        mock_service = Mock()
        mock_service_class = Mock(return_value=mock_service)
        ServiceRegistry._services["test"] = mock_service_class

        kwargs = {
            "api_key": "test_key",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 100
        }

        result = ServiceRegistry.create_service("test", **kwargs)

        assert result == mock_service
        mock_service_class.assert_called_once_with(**kwargs)


class TestConvenienceFunctions:
    """Test convenience functions."""

    def setup_method(self):
        """Set up test fixtures."""
        # Reset the registry for each test
        ServiceRegistry._services = {
            "google": Mock(),
            "anthropic": Mock(),
            "openai": Mock(),
            "ollama": Mock(),
        }

    @patch("intent_kit.services.ServiceRegistry.get_available_services")
    def test_get_available_services_function(self, mock_get_available):
        """Test get_available_services convenience function."""
        expected = {"google": True, "anthropic": False}
        mock_get_available.return_value = expected

        result = get_available_services()

        mock_get_available.assert_called_once()
        assert result == expected

    @patch("intent_kit.services.ServiceRegistry.create_service")
    def test_create_service_function(self, mock_create_service):
        """Test create_service convenience function."""
        mock_service = Mock()
        mock_create_service.return_value = mock_service

        result = create_service("test", api_key="test_key")

        mock_create_service.assert_called_once_with("test", api_key="test_key")
        assert result == mock_service


class TestServiceRegistryIntegration:
    """Integration tests for ServiceRegistry."""

    def setup_method(self):
        """Set up test fixtures."""
        # Reset the registry for each test
        ServiceRegistry._services = {
            "google": Mock(),
            "anthropic": Mock(),
            "openai": Mock(),
            "ollama": Mock(),
        }

    def test_full_workflow(self):
        """Test complete workflow of registering, checking, and creating services."""
        # Create a mock service class
        mock_service_class = Mock()
        mock_service_instance = Mock()
        mock_service_class.return_value = mock_service_instance
        mock_service_class.is_available = Mock(return_value=True)

        # Register the service
        ServiceRegistry.register_service("custom", mock_service_class)

        # Check availability
        available = ServiceRegistry.get_available_services()
        assert available["custom"] is True

        # Create the service
        result = ServiceRegistry.create_service("custom", param1="value1")
        assert result == mock_service_instance
        mock_service_class.assert_called_once_with(param1="value1")

    def test_service_without_availability_check(self):
        """Test service that doesn't implement is_available method."""
        mock_service_class = Mock()
        mock_service_instance = Mock()
        mock_service_class.return_value = mock_service_instance
        # No is_available method

        ServiceRegistry.register_service("simple", mock_service_class)

        # Should be available by default
        available = ServiceRegistry.get_available_services()
        assert available["simple"] is True

        # Should be able to create
        result = ServiceRegistry.create_service("simple")
        assert result == mock_service_instance

    def test_service_with_availability_check_false(self):
        """Test service that returns False for availability."""
        mock_service_class = Mock()
        mock_service_class.is_available = Mock(return_value=False)

        ServiceRegistry.register_service("unavailable", mock_service_class)

        # Should be unavailable
        available = ServiceRegistry.get_available_services()
        assert available["unavailable"] is False

        # Should raise when trying to create
        with pytest.raises(ImportError):
            ServiceRegistry.create_service("unavailable")

    def test_multiple_services_different_availability(self):
        """Test multiple services with different availability status."""
        # Service 1: Available
        service1_class = Mock()
        service1_class.is_available = Mock(return_value=True)
        service1_class.return_value = Mock()

        # Service 2: Unavailable
        service2_class = Mock()
        service2_class.is_available = Mock(return_value=False)

        # Service 3: No availability check
        service3_class = Mock()
        service3_class.return_value = Mock()

        ServiceRegistry.register_service("available", service1_class)
        ServiceRegistry.register_service("unavailable", service2_class)
        ServiceRegistry.register_service("no_check", service3_class)

        available = ServiceRegistry.get_available_services()
        assert available["available"] is True
        assert available["unavailable"] is False
        assert available["no_check"] is True

        # Should be able to create available and no_check services
        ServiceRegistry.create_service("available")
        ServiceRegistry.create_service("no_check")

        # Should not be able to create unavailable service
        with pytest.raises(ImportError):
            ServiceRegistry.create_service("unavailable")