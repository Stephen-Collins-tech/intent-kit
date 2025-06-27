from typing import Callable, Dict, Any, List, Optional
from intent_kit.context import IntentContext

# Single splitter function type that supports optional context
SplitterFunction = Callable[
    [str, Dict[str, Any], bool],  # Required args: user_input, taxonomies, debug
    List[Dict[str, str]]  # Return type
]  # Context is passed as optional keyword argument: context=context
