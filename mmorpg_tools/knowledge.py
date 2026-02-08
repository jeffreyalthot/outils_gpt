"""Method library to store reusable game mechanics and AI tactics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List


@dataclass
class MethodEntry:
    name: str
    description: str
    tags: List[str]
    handler: Callable[..., object]


@dataclass
class MethodLibrary:
    """Registry of game methods, rules, and AI tactics."""

    methods: Dict[str, MethodEntry] = field(default_factory=dict)

    def register(
        self,
        name: str,
        description: str,
        tags: Iterable[str],
        handler: Callable[..., object],
    ) -> None:
        self.methods[name] = MethodEntry(
            name=name,
            description=description,
            tags=list(tags),
            handler=handler,
        )

    def list_by_tag(self, tag: str) -> List[MethodEntry]:
        return [entry for entry in self.methods.values() if tag in entry.tags]

    def run(self, name: str, *args, **kwargs) -> object:
        if name not in self.methods:
            raise KeyError(f"Unknown method: {name}")
        return self.methods[name].handler(*args, **kwargs)
