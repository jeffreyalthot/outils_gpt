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
        world.log_event("move", f"{actor.entity_id}:{self.destination}", actor.entity_id)
        world.update_entity_quest_progress(
            actor.entity_id,
            f"travel:{self.destination}",
        )
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
        world.log_event(
            "attack",
            f"{self.actor_id}:{target.entity_id}:{self.damage}",
            self.actor_id,
        )
        if not target.is_alive():
            world.update_entity_quest_progress(
                self.actor_id,
                f"defeat:{target.entity_id}",
            )
            for tag in target.tags:
                world.update_entity_quest_progress(
                    self.actor_id,
                    f"defeat_tag:{tag}",
                )
        return {"status": "ok", "detail": f"hit:{target.entity_id}:{self.damage}"}


@dataclass
class Gather(Action):
    resource: str = ""
    amount: int = 1

    def execute(self, world: WorldState) -> Dict[str, str]:
        actor = world.get_entity(self.actor_id)
        if not actor:
            return {"status": "error", "detail": "actor_not_found"}
        area = world.areas.get(actor.area)
        if not area:
            return {"status": "error", "detail": "area_not_found"}
        available = area.resources.get(self.resource, 0)
        if available <= 0:
            return {"status": "error", "detail": "resource_depleted"}
        actual_amount = min(self.amount, available)
        world.adjust_area_resource(actor.area, self.resource, -actual_amount)
        actor.inventory[self.resource] = actor.inventory.get(self.resource, 0) + actual_amount
        world.log_event(
            "gather",
            f"{actor.entity_id}:{self.resource}:{actual_amount}",
            actor.entity_id,
        )
        world.update_entity_quest_progress(
            actor.entity_id,
            f"gather:{self.resource}",
            actual_amount,
        )
        return {"status": "ok", "detail": f"gathered:{self.resource}:{actual_amount}"}


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
        world.log_event(
            "craft",
            f"{actor.entity_id}:{self.output}",
            actor.entity_id,
        )
        world.update_entity_quest_progress(
            actor.entity_id,
            f"craft:{self.output}",
        )
        return {"status": "ok", "detail": f"crafted:{self.output}"}


@dataclass
class Chat(Action):
    message: str = ""

    def execute(self, world: WorldState) -> Dict[str, str]:
        actor = world.get_entity(self.actor_id)
        if not actor:
            return {"status": "error", "detail": "actor_not_found"}
        world.log_event(
            "chat",
            f"{actor.entity_id}:{self.message}",
            actor.entity_id,
        )
        return {"status": "ok", "detail": f"chat:{actor.name}:{self.message}"}


@dataclass
class Observe(Action):
    """Inspect the current area and nearby entities."""

    def execute(self, world: WorldState) -> Dict[str, str]:
        actor = world.get_entity(self.actor_id)
        if not actor:
            return {"status": "error", "detail": "actor_not_found"}
        area = world.areas.get(actor.area)
        if not area:
            return {"status": "error", "detail": "area_not_found"}
        inhabitants = [
            entity.name
            for entity in world.get_entities_in_area(actor.area)
            if entity.entity_id != actor.entity_id
        ]
        resources = ", ".join(
            f"{name}:{qty}" for name, qty in sorted(area.resources.items())
        ) or "none"
        world.log_event(
            "observe",
            f"{actor.entity_id}:{actor.area}",
            actor.entity_id,
        )
        detail = (
            f"area:{area.name}|entities:{','.join(inhabitants) or 'none'}"
            f"|resources:{resources}"
        )
        return {"status": "ok", "detail": detail}


@dataclass
class Rest(Action):
    """Recover health and mana when resting in place."""

    hp_restore: int = 10
    mana_restore: int = 5

    def execute(self, world: WorldState) -> Dict[str, str]:
        actor = world.get_entity(self.actor_id)
        if not actor:
            return {"status": "error", "detail": "actor_not_found"}
        actor.hp = min(100, actor.hp + self.hp_restore)
        actor.mana = min(50, actor.mana + self.mana_restore)
        world.log_event(
            "rest",
            f"{actor.entity_id}:{self.hp_restore}:{self.mana_restore}",
            actor.entity_id,
        )
        return {"status": "ok", "detail": "rested"}


@dataclass
class AcceptQuest(Action):
    quest_id: str = ""

    def can_execute(self, world: WorldState) -> bool:
        if not super().can_execute(world):
            return False
        return self.quest_id in world.quests

    def execute(self, world: WorldState) -> Dict[str, str]:
        if not world.assign_quest(self.actor_id, self.quest_id):
            return {"status": "error", "detail": "quest_unavailable"}
        world.log_event(
            "quest_accept",
            f"{self.actor_id}:{self.quest_id}",
            self.actor_id,
        )
        return {"status": "ok", "detail": f"quest_accepted:{self.quest_id}"}
