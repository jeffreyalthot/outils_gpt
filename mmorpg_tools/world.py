"""World state primitives for an AI-driven MMORPG."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


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
class ItemDefinition:
    """Defines an item and its properties."""

    item_id: str
    name: str
    description: str
    stackable: bool = True


@dataclass
class ResourceNode:
    """Represents a gatherable resource node in an area."""

    node_id: str
    resource: str
    amount: int
    area: str


@dataclass
class Faction:
    """Represents a faction and its reputation table."""

    faction_id: str
    name: str
    description: str
    reputation: Dict[str, int] = field(default_factory=dict)


@dataclass
class Skill:
    """Represents a skill that can be used by entities."""

    skill_id: str
    name: str
    mana_cost: int
    effect: Callable[["WorldState", "Entity", Optional["Entity"]], str]


@dataclass
class WorldState:
    """Container for current world data."""

    areas: Dict[str, Area] = field(default_factory=dict)
    entities: Dict[str, Entity] = field(default_factory=dict)
    quests: Dict[str, Quest] = field(default_factory=dict)
    items: Dict[str, ItemDefinition] = field(default_factory=dict)
    resource_nodes: Dict[str, ResourceNode] = field(default_factory=dict)
    factions: Dict[str, Faction] = field(default_factory=dict)
    skills: Dict[str, Skill] = field(default_factory=dict)
    event_log: List[str] = field(default_factory=list)
    clock: int = 0

    def add_area(self, area: Area) -> None:
        self.areas[area.name] = area

    def add_entity(self, entity: Entity) -> None:
        self.entities[entity.entity_id] = entity

    def add_quest(self, quest: Quest) -> None:
        self.quests[quest.quest_id] = quest

    def add_item(self, item: ItemDefinition) -> None:
        self.items[item.item_id] = item

    def add_resource_node(self, node: ResourceNode) -> None:
        self.resource_nodes[node.node_id] = node

    def add_faction(self, faction: Faction) -> None:
        self.factions[faction.faction_id] = faction

    def add_skill(self, skill: Skill) -> None:
        self.skills[skill.skill_id] = skill

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entities.get(entity_id)

    def record_event(self, message: str) -> None:
        self.event_log.append(message)

    def tick(self) -> None:
        self.clock += 1
