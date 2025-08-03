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
    def load(self, *args, **kwargs) -> Any:
        """Load the specified resource."""
        pass


class DatasetLoader(Loader):
    """Loader for dataset files."""

    def load(self, dataset_path: Path) -> Dict[str, Any]:
        """Load a dataset from YAML file."""
        with open(dataset_path, "r") as f:
            return yaml_service.safe_load(f)


class ModuleLoader(Loader):
    """Loader for modules and nodes."""

    def load(self, module_name: str, node_name: str) -> Optional[Any]:
        """Get a node instance from a module."""
        try:
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
