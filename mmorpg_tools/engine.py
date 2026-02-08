"""Game engine loop for applying actions and advancing time."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .actions import Action
from .ai import AgentBrain
from .world import WorldState


@dataclass
class GameEngine:
    """Simple tick-based engine for running the world."""

    world: WorldState
    brains: Dict[str, AgentBrain] = field(default_factory=dict)

    def register_brain(self, entity_id: str, brain: AgentBrain) -> None:
        self.brains[entity_id] = brain

    def apply_action(self, action: Action) -> Dict[str, str]:
        if not action.can_execute(self.world):
            self.world.record_event(
                f"action_invalid:{action.__class__.__name__}:{action.actor_id}"
            )
            return {"status": "error", "detail": "invalid_action"}
        return action.execute(self.world)

    def step(self) -> List[Dict[str, str]]:
        results: List[Dict[str, str]] = []
        for entity_id, brain in self.brains.items():
            for action in brain.decide(self.world, entity_id):
                results.append(self.apply_action(action))
        self.world.tick()
        return results
