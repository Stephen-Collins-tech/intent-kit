"""
Base LLM Client for intent-kit

This module provides a base class for all LLM client implementations.
"""





class BaseLLMClient(ABC):
    """Base class for all LLM client implementations."""

    def __init__def __init__(self, **kwargs): -> None:
        """Initialize the base client."""
        self._client: Optional[Any] = None
        self._initialize_client(**kwargs)

    @abstractmethod
    def _initialize_client(self, **kwargs) -> None:
        """Initialize the underlying client. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def get_client(self) -> Any:
        """Get the underlying client instance. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def _ensure_imported(self) -> None:
        """Ensure the required package is imported. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Generate text using the LLM model.

        Args:
            prompt: The text prompt to send to the model
            model: The model name to use (optional, uses default if not provided)

        Returns:
            Generated text response
        """
        pass

    def generate_text(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Alias for generate method (backward compatibility).

        Args:
            prompt: The text prompt to send to the model
            model: The model name to use (optional, uses default if not provided)

        Returns:
            Generated text response
        """
        return self.generate(prompt, model)

    @classmethod
    def is_available(cls) -> bool:
        """
        Check if the required package is available.

        Returns:
            True if the package is available, False otherwise
        """
        return True
