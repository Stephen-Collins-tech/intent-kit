from typing import Callable, Dict, Any, List

SplitterFunction = Callable[[str, Dict[str, Any], bool], List[Dict[str, str]]]
