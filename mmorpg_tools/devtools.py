"""Developer tools for extending the MMORPG world in runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .knowledge import MethodLibrary
from .world import Area, Entity, Quest, WorldState


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

    def register_method(
        self,
        name: str,
        description: str,
        tags: Iterable[str],
        handler,
    ) -> None:
        self.methods.register(name, description, tags, handler)

    def assign_quest_to_entity(self, entity_id: str, quest_id: str) -> bool:
        return self.world.assign_quest(entity_id, quest_id)
