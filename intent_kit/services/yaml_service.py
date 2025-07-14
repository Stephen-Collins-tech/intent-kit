"""
YAML Service: Provides safe YAML loading and dumping with clear error if PyYAML is not installed.
"""

import logging
from typing import Any, IO, Optional

logger = logging.getLogger(__name__)


class YamlService:
    def __init__(self):
        self.yaml = None
        try:
            import yaml

            self.yaml = yaml
        except ImportError:
            logger.warning(
                "PyYAML is not installed. YAML functionality will be limited. "
                "Install with: pip install PyYAML"
            )

    def safe_load(self, stream: IO[str] | str) -> Any:
        """Safely load YAML from a file-like object or string."""
        if self.yaml is None:
            raise ImportError(
                "PyYAML is required for YAML support. Install with: pip install PyYAML"
            )
        return self.yaml.safe_load(stream)

    def dump(
        self, data: Any, stream: Optional[IO[str]] = None, **kwargs
    ) -> Optional[str]:
        """Dump data to YAML format."""
        if self.yaml is None:
            raise ImportError(
                "PyYAML is required for YAML support. Install with: pip install PyYAML"
            )
        return self.yaml.dump(data, stream=stream, **kwargs)


# Singleton instance for convenience
yaml_service = YamlService()
