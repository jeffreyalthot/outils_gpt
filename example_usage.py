"""Example usage of the MMORPG tools."""

from mmorpg_tools import (
    GameDevToolkit,
    GameEngine,
    MethodLibrary,
    RuleBasedBrain,
    WorldState,
)


def main() -> None:
    world = WorldState()
    methods = MethodLibrary()
    toolkit = GameDevToolkit(world=world, methods=methods)

    toolkit.create_area("Village", "Zone de depart", ["Foret"])
    toolkit.create_area("Foret", "Zone sauvage", ["Village"])
    toolkit.spawn_entity("player-1", "Aventurier", "Village", ["player"])
    toolkit.spawn_entity("mob-1", "Loup", "Foret", ["mob"])

    methods.register(
        name="soin",
        description="Rend des points de vie",
        tags=["combat"],
        handler=lambda entity: setattr(entity, "hp", min(100, entity.hp + 15)),
    )

    engine = GameEngine(world=world)
    engine.register_brain("player-1", RuleBasedBrain(gather_resource="bois"))

    for _ in range(3):
        results = engine.step()
        print(results)


if __name__ == "__main__":
    main()
