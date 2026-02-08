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

    toolkit.create_area(
        "Village",
        "Zone de depart",
        ["Foret"],
        resources={"eau": 3},
    )
    toolkit.create_area(
        "Foret",
        "Zone sauvage",
        ["Village"],
        resources={"bois": 5},
    )
    toolkit.spawn_entity("player-1", "Aventurier", "Village", ["player"])
    toolkit.spawn_entity("mob-1", "Loup", "Foret", ["mob"])
    toolkit.add_quest(
        "quete-1",
        "Premiers pas",
        "Collecter du bois et visiter la foret.",
        objectives={"gather:bois": 2, "travel:Foret": 1},
    )
    toolkit.assign_quest_to_entity("player-1", "quete-1")

    methods.register(
        name="soin",
        description="Rend des points de vie",
        tags=["combat"],
        handler=lambda entity: setattr(entity, "hp", min(100, entity.hp + 15)),
    )

    engine = GameEngine(world=world)
    engine.register_brain("player-1", RuleBasedBrain(gather_resource="bois"))

    for _ in range(6):
        results = engine.step()
        print(results)


if __name__ == "__main__":
    main()
