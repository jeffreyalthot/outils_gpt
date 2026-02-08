"""Developer tools for extending the MMORPG world in runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .knowledge import MethodLibrary
from .world import (
    Area,
    Entity,
    Faction,
    ItemDefinition,
    Quest,
    ResourceNode,
    Skill,
    WorldState,
)


@dataclass
class GameDevToolkit:
    """Allows adding content and methods while the game is running."""

    world: WorldState
    methods: MethodLibrary

    def create_area(self, name: str, description: str, neighbors: Iterable[str]) -> Area:
        area = Area(name=name, description=description, neighbors=list(neighbors))
        self.world.add_area(area)
        return area

    def spawn_entity(self, entity_id: str, name: str, area: str, tags: Iterable[str]) -> Entity:
        entity = Entity(entity_id=entity_id, name=name, area=area, tags=list(tags))
        self.world.add_entity(entity)
        return entity

    def add_quest(
        self,
        quest_id: str,
        title: str,
        description: str,
        objectives: dict,
    ) -> Quest:
        quest = Quest(
            quest_id=quest_id,
            title=title,
            description=description,
            objectives=objectives,
        )
        self.world.add_quest(quest)
        return quest

    def add_item(
        self,
        item_id: str,
        name: str,
        description: str,
        stackable: bool = True,
    ) -> ItemDefinition:
        item = ItemDefinition(
            item_id=item_id,
            name=name,
            description=description,
            stackable=stackable,
        )
        self.world.add_item(item)
        return item

    def add_resource_node(
        self,
        node_id: str,
        resource: str,
        amount: int,
        area: str,
    ) -> ResourceNode:
        node = ResourceNode(
            node_id=node_id,
            resource=resource,
            amount=amount,
            area=area,
        )
        self.world.add_resource_node(node)
        return node

    def add_faction(
        self,
        faction_id: str,
        name: str,
        description: str,
    ) -> Faction:
        faction = Faction(
            faction_id=faction_id,
            name=name,
            description=description,
        )
        self.world.add_faction(faction)
        return faction

    def add_skill(
        self,
        skill_id: str,
        name: str,
        mana_cost: int,
        effect,
    ) -> Skill:
        skill = Skill(
            skill_id=skill_id,
            name=name,
            mana_cost=mana_cost,
            effect=effect,
        )
        self.world.add_skill(skill)
        return skill

    def register_method(
        self,
        name: str,
        description: str,
        tags: Iterable[str],
        handler,
    ) -> None:
        self.methods.register(name, description, tags, handler)
