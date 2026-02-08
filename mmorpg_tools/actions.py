"""Action system for player and AI interactions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .world import ResourceNode, WorldState


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
        node = _find_resource_node(world, actor.area, self.resource)
        if not node:
            return {"status": "error", "detail": "resource_missing"}
        if node.amount <= 0:
            return {"status": "error", "detail": "resource_depleted"}
        gathered = min(self.amount, node.amount)
        node.amount -= gathered
        actor.inventory[self.resource] = actor.inventory.get(self.resource, 0) + gathered
        world.record_event(f"{actor.name} gathered {gathered} {self.resource}")
        return {"status": "ok", "detail": f"gathered:{self.resource}:{gathered}"}


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
        world.record_event(f"{actor.name} crafted {self.output}")
        return {"status": "ok", "detail": f"crafted:{self.output}"}


@dataclass
class Chat(Action):
    message: str = ""

    def execute(self, world: WorldState) -> Dict[str, str]:
        actor = world.get_entity(self.actor_id)
        if not actor:
            return {"status": "error", "detail": "actor_not_found"}
        world.record_event(f"{actor.name} says: {self.message}")
        return {"status": "ok", "detail": f"chat:{actor.name}:{self.message}"}


@dataclass
class Rest(Action):
    hp_restore: int = 10
    mana_restore: int = 5

    def execute(self, world: WorldState) -> Dict[str, str]:
        actor = world.get_entity(self.actor_id)
        if not actor:
            return {"status": "error", "detail": "actor_not_found"}
        actor.hp = min(100, actor.hp + self.hp_restore)
        actor.mana = min(50, actor.mana + self.mana_restore)
        world.record_event(f"{actor.name} rests")
        return {
            "status": "ok",
            "detail": f"rested:hp+{self.hp_restore}:mana+{self.mana_restore}",
        }


@dataclass
class Trade(Action):
    item: str = ""
    amount: int = 1

    def can_execute(self, world: WorldState) -> bool:
        actor = world.get_entity(self.actor_id)
        target = world.get_entity(self.target_id or "")
        return bool(actor and target and actor.area == target.area)

    def execute(self, world: WorldState) -> Dict[str, str]:
        actor = world.get_entity(self.actor_id)
        target = world.get_entity(self.target_id or "")
        if not actor or not target:
            return {"status": "error", "detail": "entity_not_found"}
        if actor.inventory.get(self.item, 0) < self.amount:
            return {"status": "error", "detail": "insufficient_items"}
        actor.inventory[self.item] -= self.amount
        target.inventory[self.item] = target.inventory.get(self.item, 0) + self.amount
        world.record_event(f"{actor.name} traded {self.amount} {self.item} to {target.name}")
        return {"status": "ok", "detail": f"traded:{self.item}:{self.amount}"}


@dataclass
class UseSkill(Action):
    skill_id: str = ""

    def execute(self, world: WorldState) -> Dict[str, str]:
        actor = world.get_entity(self.actor_id)
        if not actor:
            return {"status": "error", "detail": "actor_not_found"}
        skill = world.skills.get(self.skill_id)
        if not skill:
            return {"status": "error", "detail": "skill_missing"}
        if actor.mana < skill.mana_cost:
            return {"status": "error", "detail": "insufficient_mana"}
        target = world.get_entity(self.target_id or "") if self.target_id else None
        actor.mana -= skill.mana_cost
        result = skill.effect(world, actor, target)
        world.record_event(f"{actor.name} used {skill.name}")
        return {"status": "ok", "detail": f"skill:{skill.skill_id}:{result}"}


def _find_resource_node(
    world: WorldState,
    area: str,
    resource: str,
) -> Optional[ResourceNode]:
    for node in world.resource_nodes.values():
        if node.area == area and node.resource == resource:
            return node
    return None
