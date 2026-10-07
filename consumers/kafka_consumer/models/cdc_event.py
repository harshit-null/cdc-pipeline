from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CDCEvent:
    """Represents a Change Data Capture (CDC) event."""

    operation: str
    before: Optional[dict[str, Any]] = None
    after: Optional[dict[str, Any]] = None
    source: Optional[dict[str, Any]] = None
    timestamp: Optional[int] = None

    @classmethod
    def from_dict(cls, event: dict[str, Any]) -> "CDCEvent":
        """Creates a CDCEvent instance from a dictionary."""

        return cls(
            operation=event.get("op"),
            before=event.get("before"),
            after=event.get("after"),
            source=event.get("source"),
            timestamp=event.get("ts_ms"),
        )

    @property
    def is_create(self) -> bool:
        return self.operation == "c"

    @property
    def is_update(self) -> bool:
        return self.operation == "u"

    @property
    def is_delete(self) -> bool:
        return self.operation == "d"

    @property
    def is_snapshot(self) -> bool:
        return self.operation == "r"

    @property
    def product(self) -> Optional[dict[str, Any]]:
        """
        Returns the relevant product payload.

        CREATE / UPDATE / SNAPSHOT -> after
        DELETE -> before
        """

        if self.is_delete:
            return self.before

        return self.after