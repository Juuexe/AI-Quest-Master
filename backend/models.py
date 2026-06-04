from dataclasses import asdict, dataclass, field


@dataclass
class Player:
    name: str
    character_class: str
    health: int
    inventory: list[str] = field(default_factory=list)

    def get_status(self) -> str:
        inventory_text = ", ".join(self.inventory) if self.inventory else "empty"
        return (
            f"Player name: {self.name}\n"
            f"Class: {self.character_class}\n"
            f"Health: {self.health}\n"
            f"Inventory: {inventory_text}"
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        return cls(
            name=data["name"],
            character_class=data["character_class"],
            health=int(data["health"]),
            inventory=list(data.get("inventory", [])),
        )


@dataclass
class GameState:
    player: Player
    current_story: str
    turn_count: int = 0
    game_over: bool = False
    last_event: str = ""

    def to_dict(self) -> dict:
        return {
            "player": self.player.to_dict(),
            "current_story": self.current_story,
            "turn_count": self.turn_count,
            "game_over": self.game_over,
            "last_event": self.last_event,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        return cls(
            player=Player.from_dict(data["player"]),
            current_story=data.get("current_story", ""),
            turn_count=int(data.get("turn_count", 0)),
            game_over=bool(data.get("game_over", False)),
            last_event=data.get("last_event", ""),
        )

