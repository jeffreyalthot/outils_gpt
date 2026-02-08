"""AI logic helpers for autonomous agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .actions import Action, Move, Attack, Gather
from .world import WorldState


class AgentBrain:
    """Base class for AI brains."""

    def decide(self, world: WorldState, actor_id: str) -> List[Action]:
        raise NotImplementedError


@dataclass
class RuleBasedBrain(AgentBrain):
    """Simple rule-based behavior for testing worlds."""

    gather_resource: str = "bois"

    def decide(self, world: WorldState, actor_id: str) -> List[Action]:
        actor = world.get_entity(actor_id)
        if not actor:
            return []
        for entity in world.entities.values():
            if (
                entity.entity_id != actor_id
                and entity.area == actor.area
                and entity.is_alive()
            ):
                return [Attack(actor_id=actor_id, target_id=entity.entity_id, damage=8)]
        area = world.areas.get(actor.area)
        if area and area.neighbors:
            return [Move(actor_id=actor_id, destination=area.neighbors[0])]
        return [Gather(actor_id=actor_id, resource=self.gather_resource, amount=1)]
