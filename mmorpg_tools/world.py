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
    resources: Dict[str, int] = field(default_factory=dict)


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
    quest_log: Dict[str, "QuestProgress"] = field(default_factory=dict)

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
class QuestProgress:
    """Tracks quest progress for a specific entity."""

    quest_id: str
    progress: Dict[str, int] = field(default_factory=dict)
    completed: bool = False

    def update(self, quest: Quest, objective: str, amount: int = 1) -> None:
        current = self.progress.get(objective, 0)
        self.progress[objective] = current + amount
        if all(
            self.progress.get(key, 0) >= required
            for key, required in quest.objectives.items()
        ):
            self.completed = True


@dataclass
class WorldEvent:
    """Represents a logged event in the world."""

    tick: int
    kind: str
    detail: str
    actor_id: Optional[str] = None


@dataclass
class WorldState:
    """Container for current world data."""

    areas: Dict[str, Area] = field(default_factory=dict)
    entities: Dict[str, Entity] = field(default_factory=dict)
    quests: Dict[str, Quest] = field(default_factory=dict)
    events: List[WorldEvent] = field(default_factory=list)
    clock: int = 0

    def add_area(self, area: Area) -> None:
        self.areas[area.name] = area

    def add_entity(self, entity: Entity) -> None:
        self.entities[entity.entity_id] = entity

    def add_quest(self, quest: Quest) -> None:
        self.quests[quest.quest_id] = quest

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entities.get(entity_id)

    def get_entities_in_area(self, area_name: str) -> List[Entity]:
        return [entity for entity in self.entities.values() if entity.area == area_name]

    def get_recent_events(self, limit: int = 5) -> List[WorldEvent]:
        if limit <= 0:
            return []
        return self.events[-limit:]

    def assign_quest(self, entity_id: str, quest_id: str) -> bool:
        entity = self.entities.get(entity_id)
        quest = self.quests.get(quest_id)
        if not entity or not quest:
            return False
        if quest_id in entity.quest_log:
            return False
        entity.quest_log[quest_id] = QuestProgress(quest_id=quest_id)
        return True

    def adjust_area_resource(self, area_name: str, resource: str, delta: int) -> int:
        area = self.areas.get(area_name)
        if not area:
            return 0
        current = area.resources.get(resource, 0)
        new_value = max(0, current + delta)
        area.resources[resource] = new_value
        return new_value

    def update_entity_quest_progress(
        self,
        entity_id: str,
        objective: str,
        amount: int = 1,
    ) -> None:
        entity = self.entities.get(entity_id)
        if not entity:
            return
        for quest_id, progress in entity.quest_log.items():
            quest = self.quests.get(quest_id)
            if not quest or progress.completed:
                continue
            if objective in quest.objectives:
                progress.update(quest, objective, amount)

    def log_event(self, kind: str, detail: str, actor_id: Optional[str] = None) -> None:
        self.events.append(
            WorldEvent(tick=self.clock, kind=kind, detail=detail, actor_id=actor_id)
        )

    def tick(self) -> None:
        self.clock += 1
