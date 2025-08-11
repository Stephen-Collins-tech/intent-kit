"""
Tests for BaseContext abstraction.

This module tests the BaseContext ABC and its implementations.
"""

from typing import List
from intent_kit.context import BaseContext, Context, StackContext


class TestBaseContext:
    """Test the BaseContext abstract base class."""

    def test_base_context_initialization(self):
        """Test that BaseContext can be initialized with session_id and debug."""
        # This should work since we're testing the concrete implementations
        context = Context(session_id="test-session")
        assert context.session_id == "test-session"

    def test_base_context_string_representation(self):
        """Test string representation of BaseContext implementations."""
        context = Context(session_id="test-session")
        assert "Context" in str(context)
        assert "test-session" in str(context)

    def test_base_context_session_management(self):
        """Test session ID management."""
        context = Context()
        session_id = context.get_session_id()
        assert session_id is not None
        assert len(session_id) > 0

    def test_base_context_abstract_methods_implementation(self):
        """Test that all abstract methods are implemented."""
        context = Context()

        # Test error count
        assert isinstance(context.get_error_count(), int)

        # Test add_error
        context.add_error("test_node", "test_input", "test_error", "test_type")
        assert context.get_error_count() == 1

        # Test get_errors
        errors = context.get_errors()
        assert isinstance(errors, list)
        assert len(errors) == 1

        # Test clear_errors
        context.clear_errors()
        assert context.get_error_count() == 0

        # Test get_history
        history = context.get_history()
        assert isinstance(history, list)

        # Test export_to_dict
        export = context.export_to_dict()
        assert isinstance(export, dict)
        assert "session_id" in export


class TestContextInheritance:
    """Test that Context properly inherits from BaseContext."""

    def test_context_inheritance(self):
        """Test that Context is a subclass of BaseContext."""
        assert issubclass(Context, BaseContext)

    def test_context_legacy_methods(self):
        """Test that legacy methods still work."""
        context = Context()
        context.add_error("test_node", "test_input", "test_error", "test_type")

        # Test legacy error_count method
        assert context.error_count() == 1
        assert context.get_error_count() == 1

    def test_context_export_to_dict(self):
        """Test Context's export_to_dict implementation."""
        context = Context(session_id="test-session")
        context.set("test_key", "test_value", "test_user")

        export = context.export_to_dict()
        assert export["session_id"] == "test-session"
        assert "test_key" in export["fields"]
        assert export["fields"]["test_key"]["value"] == "test_value"


class TestStackContextInheritance:
    """Test that StackContext properly inherits from BaseContext."""

    def test_stack_context_inheritance(self):
        """Test that StackContext is a subclass of BaseContext."""
        assert issubclass(StackContext, BaseContext)

    def test_stack_context_delegation(self):
        """Test that StackContext delegates to underlying Context."""
        base_context = Context(session_id="test-session")
        stack_context = StackContext(base_context)

        # Test that session_id is shared
        assert stack_context.session_id == base_context.session_id

        # Test error delegation
        stack_context.add_error("test_node", "test_input", "test_error", "test_type")
        assert stack_context.get_error_count() == 1
        assert base_context.get_error_count() == 1

        # Test error clearing delegation
        stack_context.clear_errors()
        assert stack_context.get_error_count() == 0
        assert base_context.get_error_count() == 0

    def test_stack_context_export_to_dict(self):
        """Test StackContext's export_to_dict implementation."""
        base_context = Context(session_id="test-session")
        stack_context = StackContext(base_context)

        # Add some frames
        frame_id = stack_context.push_frame(
            "test_function",
            "test_node",
            ["root", "test_node"],
            "test_input",
            {"param": "value"},
        )

        export = stack_context.export_to_dict()
        assert export["session_id"] == "test-session"
        assert export["total_frames"] == 1
        assert "frames" in export
        assert len(export["frames"]) == 1
        assert export["frames"][0]["frame_id"] == frame_id


class TestBaseContextPolymorphism:
    """Test polymorphic behavior of BaseContext implementations."""

    def test_polymorphic_error_handling(self):
        """Test that different context types handle errors polymorphically."""
        contexts: List[BaseContext] = [
            Context(session_id="test-session"),
            StackContext(Context(session_id="test-session")),
        ]

        for context in contexts:
            # Test error addition
            context.add_error("test_node", "test_input", "test_error", "test_type")
            assert context.get_error_count() == 1

            # Test error retrieval
            errors = context.get_errors()
            assert len(errors) == 1
            assert errors[0].node_name == "test_node"

            # Test error clearing
            context.clear_errors()
            assert context.get_error_count() == 0

    def test_polymorphic_history_handling(self):
        """Test that different context types handle history polymorphically."""
        contexts: List[BaseContext] = [
            Context(session_id="test-session"),
            StackContext(Context(session_id="test-session")),
        ]

        for context in contexts:
            # Test history retrieval
            history = context.get_history()
            assert isinstance(history, list)

            # Test history with limit
            limited_history = context.get_history(limit=5)
            assert isinstance(limited_history, list)

    def test_polymorphic_export(self):
        """Test that different context types can export polymorphically."""
        contexts: List[BaseContext] = [
            Context(session_id="test-session"),
            StackContext(Context(session_id="test-session")),
        ]

        for context in contexts:
            export = context.export_to_dict()
            assert isinstance(export, dict)
            assert "session_id" in export
            assert export["session_id"] == "test-session"


class TestBaseContextIntegration:
    """Test integration between BaseContext implementations."""

    def test_context_stack_context_integration(self):
        """Test that Context and StackContext work together seamlessly."""
        # Create base context
        base_context = Context(session_id="test-session")

        # Create stack context that wraps the base context
        stack_context = StackContext(base_context)

        # Verify they share the same session
        assert base_context.session_id == stack_context.session_id

        # Add data to base context
        base_context.set("test_key", "test_value", "test_user")

        # Add error through stack context
        stack_context.add_error("test_node", "test_input", "test_error", "test_type")

        # Verify both contexts see the same state
        assert base_context.get("test_key") == "test_value"
        assert base_context.get_error_count() == 1
        assert stack_context.get_error_count() == 1

        # Verify stack context can access base context data
        errors = stack_context.get_errors()
        assert len(errors) == 1
        assert errors[0].node_name == "test_node"

    def test_base_context_interface_consistency(self):
        """Test that all BaseContext implementations provide consistent interfaces."""
        base_context = Context(session_id="test-session")
        stack_context = StackContext(base_context)

        # Test that both implement the same interface
        for context in [base_context, stack_context]:
            # Test required methods exist
            assert hasattr(context, "get_error_count")
            assert hasattr(context, "add_error")
            assert hasattr(context, "get_errors")
            assert hasattr(context, "clear_errors")
            assert hasattr(context, "get_history")
            assert hasattr(context, "export_to_dict")

            # Test utility methods exist
            assert hasattr(context, "get_session_id")
            assert hasattr(context, "log_debug")
            assert hasattr(context, "log_info")
            assert hasattr(context, "log_error")
