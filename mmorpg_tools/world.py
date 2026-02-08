"""World state primitives for an AI-driven MMORPG."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Area:
    """Represents a named area in the world map."""

    name: str
    description: str
    neighbors: List[str] = field(default_factory=list)


@dataclass
class Entity:
    """Represents a player, NPC, or creature in the world."""

    entity_id: str
    name: str
    area: str
    hp: int = 100
    mana: int = 50
    inventory: Dict[str, int] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def is_alive(self) -> bool:
        return self.hp > 0


@dataclass
class Quest:
    """Represents a quest definition and its progress."""

    quest_id: str
    title: str
    description: str
    objectives: Dict[str, int]
    progress: Dict[str, int] = field(default_factory=dict)
    completed: bool = False

    def update_progress(self, objective: str, amount: int = 1) -> None:
        current = self.progress.get(objective, 0)
        self.progress[objective] = current + amount
        if all(
            self.progress.get(key, 0) >= required
            for key, required in self.objectives.items()
        ):
            self.completed = True


@dataclass
class WorldState:
    """Container for current world data."""

    areas: Dict[str, Area] = field(default_factory=dict)
    entities: Dict[str, Entity] = field(default_factory=dict)
    quests: Dict[str, Quest] = field(default_factory=dict)
    clock: int = 0

    def add_area(self, area: Area) -> None:
        self.areas[area.name] = area

    def add_entity(self, entity: Entity) -> None:
        self.entities[entity.entity_id] = entity

    def add_quest(self, quest: Quest) -> None:
        self.quests[quest.quest_id] = quest

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entities.get(entity_id)

    def tick(self) -> None:
        self.clock += 1
