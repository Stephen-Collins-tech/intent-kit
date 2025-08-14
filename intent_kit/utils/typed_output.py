"""
Typed output utilities for handling different output formats.
"""

from dataclasses import dataclass
from typing import Dict, Any

from intent_kit.types import TypedOutputType, IntentClassification, IntentAction

# Try to import yaml at module load time
try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


@dataclass
class TypedOutputData:
    """A typed output with content and type information."""

    content: Any
    type: TypedOutputType = TypedOutputType.AUTO

    def get_typed_content(self) -> Any:
        """Get the content cast to the specified type."""
        if self.type == TypedOutputType.AUTO:
            return self._auto_detect_type()
        elif self.type == TypedOutputType.JSON:
            return self._cast_to_json()
        elif self.type == TypedOutputType.YAML:
            return self._cast_to_yaml()
        elif self.type == TypedOutputType.STRING:
            return self._cast_to_string()
        elif self.type == TypedOutputType.DICT:
            return self._cast_to_dict()
        elif self.type == TypedOutputType.LIST:
            return self._cast_to_list()
        elif self.type == TypedOutputType.CLASSIFIER:
            return self._cast_to_classifier()
        else:
            return self.content

    def _auto_detect_type(self) -> Any:
        """Automatically detect the type of content."""
        if isinstance(self.content, (dict, list)):
            return self.content
        elif isinstance(self.content, str):
            # Try to parse as JSON
            try:
                import json

                return json.loads(self.content)
            except (json.JSONDecodeError, ValueError):
                # Try to parse as YAML
                if yaml is not None:
                    try:
                        parsed = yaml.safe_load(self.content)
                        if isinstance(parsed, (dict, list)):
                            return parsed
                        else:
                            return {"raw_content": self.content}
                    except (yaml.YAMLError, ValueError):
                        pass
                return {"raw_content": self.content}
        else:
            return {"raw_content": str(self.content)}

    def _cast_to_json(self) -> Any:
        """Cast content to JSON format."""
        if isinstance(self.content, str):
            try:
                import json

                return json.loads(self.content)
            except (json.JSONDecodeError, ValueError):
                return {"raw_content": self.content}
        elif isinstance(self.content, (dict, list)):
            return self.content
        else:
            return {"raw_content": str(self.content)}

    def _cast_to_yaml(self) -> Any:
        """Cast content to YAML format."""
        if isinstance(self.content, str):
            if yaml is not None:
                try:
                    parsed = yaml.safe_load(self.content)
                    if isinstance(parsed, (dict, list)):
                        return parsed
                    else:
                        return {"raw_content": self.content}
                except (yaml.YAMLError, ValueError):
                    pass
            return {"raw_content": self.content}
        elif isinstance(self.content, (dict, list)):
            return self.content
        else:
            return {"raw_content": str(self.content)}

    def _cast_to_string(self) -> str:
        """Cast content to string format."""
        if isinstance(self.content, str):
            return self.content
        else:
            import json

            return json.dumps(self.content, indent=2)

    def _cast_to_dict(self) -> Dict[str, Any]:
        """Cast content to dictionary format."""
        if isinstance(self.content, dict):
            return self.content
        elif isinstance(self.content, str):
            try:
                import json

                parsed = json.loads(self.content)
                if isinstance(parsed, dict):
                    return parsed
                else:
                    return {"raw_content": self.content}
            except (json.JSONDecodeError, ValueError):
                try:
                    import yaml

                    parsed = yaml.safe_load(self.content)
                    if isinstance(parsed, dict):
                        return parsed
                    else:
                        return {"raw_content": self.content}
                except (yaml.YAMLError, ValueError, ImportError):
                    return {"raw_content": self.content}
        else:
            return {"raw_content": str(self.content)}

    def _cast_to_list(self) -> list:
        """Cast content to list format."""
        if isinstance(self.content, list):
            return self.content
        elif isinstance(self.content, str):
            try:
                import json

                parsed = json.loads(self.content)
                if isinstance(parsed, list):
                    return parsed
                else:
                    return [self.content]
            except (json.JSONDecodeError, ValueError):
                try:
                    import yaml

                    parsed = yaml.safe_load(self.content)
                    if isinstance(parsed, list):
                        return parsed
                    else:
                        return [self.content]
                except (yaml.YAMLError, ValueError, ImportError):
                    return [self.content]
        else:
            return [str(self.content)]

    def _cast_to_classifier(self) -> "ClassifierOutput":
        """Cast content to ClassifierOutput type."""
        if isinstance(self.content, dict):
            # Try to convert dict to ClassifierOutput
            return self._dict_to_classifier_output(self.content)
        elif isinstance(self.content, str):
            # Try to parse as JSON first
            try:
                import json

                parsed = json.loads(self.content)
                if isinstance(parsed, dict):
                    return self._dict_to_classifier_output(parsed)
                else:
                    return self._create_default_classifier_output(self.content)
            except (json.JSONDecodeError, ValueError):
                # Try YAML
                try:
                    import yaml

                    parsed = yaml.safe_load(self.content)
                    if isinstance(parsed, dict):
                        return self._dict_to_classifier_output(parsed)
                    else:
                        return self._create_default_classifier_output(self.content)
                except (yaml.YAMLError, ValueError, ImportError):
                    return self._create_default_classifier_output(self.content)
        else:
            return self._create_default_classifier_output(str(self.content))

    def _dict_to_classifier_output(self, data: Dict[str, Any]) -> "ClassifierOutput":
        """Convert a dictionary to ClassifierOutput."""
        # Extract fields from the dict
        chunk_text = data.get("chunk_text", "")
        classification_str = data.get("classification", "Atomic")
        intent_type = data.get("intent_type")
        action_str = data.get("action", "handle")
        metadata = data.get("metadata", {})

        # Convert classification string to enum
        try:
            classification = IntentClassification(classification_str)
        except ValueError:
            classification = IntentClassification.ATOMIC

        # Convert action string to enum
        try:
            action = IntentAction(action_str)
        except ValueError:
            action = IntentAction.HANDLE

        return {
            "chunk_text": chunk_text,
            "classification": classification,
            "intent_type": intent_type,
            "action": action,
            "metadata": metadata,
        }

    def _create_default_classifier_output(self, content: str) -> "ClassifierOutput":
        """Create a default ClassifierOutput from content."""
        return {
            "chunk_text": content,
            "classification": IntentClassification.ATOMIC,
            "intent_type": None,
            "action": IntentAction.HANDLE,
            "metadata": {"raw_content": content},
        }


# Type alias for ClassifierOutput
ClassifierOutput = Dict[str, Any]
