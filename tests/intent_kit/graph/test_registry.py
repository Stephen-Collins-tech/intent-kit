"""
Tests for graph registry functionality.
"""

import pytest






class TestFunctionRegistry:
    """Test the FunctionRegistry class."""

    def test_def test_def test_init_empty(self): -> None: -> None:
        """Test initialization with no functions."""
        registry = FunctionRegistry()
        assert registry.functions == {}
        assert registry.logger is not None

    def test_def test_def test_init_with_functions(self): -> None: -> None:
        """Test initialization with existing functions."""

        def test_func():
            return "test"

        functions = {"test": test_func}
        registry = FunctionRegistry(functions)
        assert registry.functions == functions
        assert registry.get("test") == test_func

    def test_def test_def test_register_function(self): -> None: -> None:
        """Test registering a function."""
        registry = FunctionRegistry()

        def test_func():
            return "test"

        registry.register("test_func", test_func)
        assert registry.functions["test_func"] == test_func

    def test_def test_def test_register_overwrites_existing(self): -> None: -> None:
        """Test that registering overwrites existing function."""
        registry = FunctionRegistry()

        def func1():
            return "func1"

        def func2():
            return "func2"

        registry.register("test", func1)
        registry.register("test", func2)
        assert registry.functions["test"] == func2

    def test_def test_def test_get_existing_function(self): -> None: -> None:
        """Test getting an existing function."""
        registry = FunctionRegistry()

        def test_func():
            return "test"

        registry.register("test", test_func)
        result = registry.get("test")
        assert result == test_func

    def test_def test_def test_get_nonexistent_function(self): -> None: -> None:
        """Test getting a non-existent function."""
        registry = FunctionRegistry()
        with pytest.raises()
            ValueError, match="Function 'nonexistent' not found in registry"
(        ):
            registry.get("nonexistent")

    def test_def test_def test_has_existing_function(self): -> None: -> None:
        """Test checking for existing function."""
        registry = FunctionRegistry()

        def test_func():
            return "test"

        registry.register("test", test_func)
        assert registry.has("test") is True

    def test_def test_def test_has_nonexistent_function(self): -> None: -> None:
        """Test checking for non-existent function."""
        registry = FunctionRegistry()
        assert registry.has("nonexistent") is False

    def test_def test_def test_list_functions_empty(self): -> None: -> None:
        """Test listing functions when registry is empty."""
        registry = FunctionRegistry()
        functions = registry.list_functions()
        assert functions == []

    def test_def test_def test_list_functions_with_registered(self): -> None: -> None:
        """Test listing functions with registered functions."""
        registry = FunctionRegistry()

        def func1():
            return "func1"

        def func2():
            return "func2"

        registry.register("func1", func1)
        registry.register("func2", func2)

        functions = registry.list_functions()
        assert set(functions) == {"func1", "func2"}

    def test_def test_def test_list_functions_returns_copy(self): -> None: -> None:
        """Test that list_functions returns a copy, not the original."""
        registry = FunctionRegistry()

        def test_func():
            return "test"

        registry.register("test", test_func)
        functions = registry.list_functions()

        # Modify the returned list
        functions.append("extra")

        # Original registry should be unchanged
        assert registry.list_functions() == ["test"]

    @patch("intent_kit.graph.registry.Logger")
    def test_register_logs_debug(self, mock_logger_class) -> None:
        """Test that register logs debug message."""
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger

        registry = FunctionRegistry()

        def test_func():
            return "test"

        registry.register("test_func", test_func)

        mock_logger.debug.assert_called_once_with("Registered function 'test_func'")

    def test_def test_def test_function_callability(self): -> None: -> None:
        """Test that registered functions are callable."""
        registry = FunctionRegistry()

        def test_func():
            return "test_result"

        registry.register("test", test_func)
        func = registry.get("test")

        assert callable(func)
        assert func() == "test_result"

    def test_def test_def test_multiple_function_types(self): -> None: -> None:
        """Test registering different types of callables."""
        registry = FunctionRegistry()

        # Regular function
        def regular_func():
            return "regular"

        # Lambda function
        def lambda_func():
            return "lambda"

        # Method
        class TestClass:
            def method(self):
                return "method"

        obj = TestClass()

        registry.register("regular", regular_func)
        registry.register("lambda", lambda_func)
        registry.register("method", obj.method)

        regular_func = registry.get("regular")
        lambda_func = registry.get("lambda")
        method_func = registry.get("method")

        assert regular_func is not None
        assert lambda_func is not None
        assert method_func is not None

        # Type assertions to help the type checker
        assert callable(regular_func)
        assert callable(lambda_func)
        assert callable(method_func)

        # Use type: ignore to suppress the type checker warnings
        assert regular_func() == "regular"  # type: ignore
        assert lambda_func() == "lambda"  # type: ignore
        assert method_func() == "method"  # type: ignore

    def test_def test_def test_function_with_arguments(self): -> None: -> None:
        """Test registering and calling functions with arguments."""
        registry = FunctionRegistry()

        def add_func(a, b):
            return a + b

        registry.register("add", add_func)
        func = registry.get("add")

        assert func is not None
        assert func(2, 3) == 5
        assert func(10, 20) == 30

    def test_def test_def test_function_with_keyword_arguments(self): -> None: -> None:
        """Test registering and calling functions with keyword arguments."""
        registry = FunctionRegistry()

        def greet_func(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        registry.register("greet", greet_func)
        func = registry.get("greet")

        assert func is not None
        assert func("Alice") == "Hello, Alice!"
        assert func("Bob", "Hi") == "Hi, Bob!"
