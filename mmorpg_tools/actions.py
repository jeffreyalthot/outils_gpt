"""Action system for player and AI interactions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .world import WorldState


@dataclass
class Action:
    """Base class for actions."""

    actor_id: str
    target_id: Optional[str] = None

    def can_execute(self, world: WorldState) -> bool:
        return world.get_entity(self.actor_id) is not None

    def execute(self, world: WorldState) -> Dict[str, str]:
        raise NotImplementedError


@dataclass
class Move(Action):
    destination: str = ""

    def can_execute(self, world: WorldState) -> bool:
        actor = world.get_entity(self.actor_id)
        if not actor:
            return False
        if self.destination not in world.areas:
            return False
        current_area = world.areas.get(actor.area)
        return self.destination in (current_area.neighbors if current_area else [])

    def execute(self, world: WorldState) -> Dict[str, str]:
        actor = world.get_entity(self.actor_id)
        if not actor:
            return {"status": "error", "detail": "actor_not_found"}
        actor.area = self.destination
        return {"status": "ok", "detail": f"moved_to:{self.destination}"}


@dataclass
class Attack(Action):
    damage: int = 10

    def can_execute(self, world: WorldState) -> bool:
        actor = world.get_entity(self.actor_id)
        target = world.get_entity(self.target_id or "")
        return bool(actor and target and actor.area == target.area and target.is_alive())

    def execute(self, world: WorldState) -> Dict[str, str]:
        target = world.get_entity(self.target_id or "")
        if not target:
            return {"status": "error", "detail": "target_not_found"}
        target.hp = max(0, target.hp - self.damage)
        return {"status": "ok", "detail": f"hit:{target.entity_id}:{self.damage}"}


@dataclass
class Gather(Action):
    resource: str = ""
    amount: int = 1

    def execute(self, world: WorldState) -> Dict[str, str]:
        actor = world.get_entity(self.actor_id)
        if not actor:
            return {"status": "error", "detail": "actor_not_found"}
        actor.inventory[self.resource] = actor.inventory.get(self.resource, 0) + self.amount
        return {"status": "ok", "detail": f"gathered:{self.resource}:{self.amount}"}


@dataclass
class Craft(Action):
    recipe: str = ""
    output: str = ""
    requirements: Dict[str, int] = None

    def execute(self, world: WorldState) -> Dict[str, str]:
        actor = world.get_entity(self.actor_id)
        if not actor:
            return {"status": "error", "detail": "actor_not_found"}
        requirements = self.requirements or {}
        for item, qty in requirements.items():
            if actor.inventory.get(item, 0) < qty:
                return {"status": "error", "detail": "missing_materials"}
        for item, qty in requirements.items():
            actor.inventory[item] -= qty
        actor.inventory[self.output] = actor.inventory.get(self.output, 0) + 1
        return {"status": "ok", "detail": f"crafted:{self.output}"}


@dataclass
class Chat(Action):
    message: str = ""

    def execute(self, world: WorldState) -> Dict[str, str]:
        actor = world.get_entity(self.actor_id)
        if not actor:
            return {"status": "error", "detail": "actor_not_found"}
        return {"status": "ok", "detail": f"chat:{actor.name}:{self.message}"}
