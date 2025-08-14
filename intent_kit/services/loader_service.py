"""
Loader service for loading datasets and modules.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
import importlib
from intent_kit.services.yaml_service import yaml_service


class Loader(ABC):
    """Base class for loaders."""

    @abstractmethod
    def load(self, path: Path) -> Any:
        """Load the specified resource."""


class DatasetLoader(Loader):
    """Loader for dataset files."""

    def load(self, path: Path) -> Dict[str, Any]:
        """Load a dataset from YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            return yaml_service.safe_load(f)


class ModuleLoader(Loader):
    """Loader for modules and nodes."""

    def load(self, path: Path) -> Optional[Any]:
        """Get a node instance from a module path."""
        try:
            # Parse path as module_name:node_name
            parts = str(path).split(":", 1)
            if len(parts) != 2:
                raise ValueError(
                    f"Invalid module path format: {path}. Expected 'module_name:node_name'"
                )

            module_name, node_name = parts
            module = importlib.import_module(module_name)
            node_func = getattr(module, node_name)
            # Call the function to get the node instance
            if callable(node_func):
                return node_func()
            else:
                return node_func
        except (ImportError, AttributeError) as e:
            print(f"Error loading node {node_name} from {module_name}: {e}")
            return None


# Create singleton instances
dataset_loader = DatasetLoader()
module_loader = ModuleLoader()
