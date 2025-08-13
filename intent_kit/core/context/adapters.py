from __future__ import annotations

from typing import Any, Mapping, Optional

from intent_kit.core.context.default import DefaultContext
from intent_kit.core.context.protocols import LoggerLike
from intent_kit.utils.logger import Logger


class DictBackedContext(DefaultContext):
    """
    Adapter that hydrates from an existing dict-like context once,
    then behaves like DefaultContext.

    This is intended as a back-compat shim during migration.
    """

    def __init__(
        self,
        backing: Optional[Mapping[str, Any]],
        *,
        logger: Optional[LoggerLike] = None,
    ) -> None:
        super().__init__(logger=logger or Logger("intent_kit.context.dict_backed"))
        # Single hydration step
        if backing is not None:
            for k, v in backing.items():
                if isinstance(k, str):
                    self._data[k] = v
