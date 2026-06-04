import random

from models import GameState, Player


VALID_CLASSES = {
    "warrior": {
        "display": "Warrior",
        "health": 120,
        "inventory": ["sword", "shield", "health potion"],
    },
    "mage": {
        "display": "Mage",
        "health": 80,
        "inventory": ["staff", "mana potion", "spell book"],
    },
    "rogue": {
        "display": "Rogue",
        "health": 100,
        "inventory": ["dagger", "lockpick", "smoke bomb"],
    },
}

VALID_CHOICES = {"A", "B", "C"}


def normalize_class(character_class: str) -> str | None:
    cleaned = character_class.strip().lower()
    if cleaned in VALID_CLASSES:
        return VALID_CLASSES[cleaned]["display"]
    return None


def create_player(name: str, character_class: str) -> Player:
    normalized = character_class.strip().lower()
    if normalized not in VALID_CLASSES:
        raise ValueError("Invalid class. Please choose Warrior, Mage, or Rogue.")

    class_data = VALID_CLASSES[normalized]
    clean_name = name.strip() or "Hero"
    return Player(
        name=clean_name,
        character_class=class_data["display"],
        health=class_data["health"],
        inventory=list(class_data["inventory"]),
    )


def is_valid_choice(choice: str) -> bool:
    return choice.strip().upper() in VALID_CHOICES


def apply_random_health_event(game_state: GameState) -> str:
    if game_state.game_over:
        return ""

    roll = random.randint(1, 100)
    damage = 0
    event = ""

    if roll <= 18:
        damage = random.randint(5, 16)
        event = f"A hidden danger strikes. You lose {damage} health."
    elif roll >= 93:
        healing = random.randint(4, 10)
        before = game_state.player.health
        game_state.player.health = min(before + healing, max_health_for(game_state.player))
        event = f"You catch your breath and recover {game_state.player.health - before} health."

    if damage:
        game_state.player.health = max(0, game_state.player.health - damage)
        if game_state.player.health == 0:
            game_state.game_over = True
            event += " Your health has reached 0. Your quest ends here."

    game_state.last_event = event
    return event


def max_health_for(player: Player) -> int:
    class_key = player.character_class.lower()
    return VALID_CLASSES.get(class_key, {"health": 100})["health"]


def use_health_potion(game_state: GameState) -> str:
    player = game_state.player
    potion = next((item for item in player.inventory if item.lower() == "health potion"), None)
    if not potion:
        return "You do not have a health potion."

    if player.health >= max_health_for(player):
        return "Your health is already full."

    player.inventory.remove(potion)
    before = player.health
    player.health = min(max_health_for(player), player.health + 30)
    return f"You use a health potion and recover {player.health - before} health."


def build_opening_prompt(player: Player) -> str:
    return (
        "Start a new fantasy RPG adventure for this player.\n\n"
        f"{player.get_status()}\n\n"
        "Create the opening scene and exactly three choices."
    )


def build_choice_prompt(game_state: GameState, choice: str) -> str:
    event_text = f"\nRecent game event: {game_state.last_event}\n" if game_state.last_event else ""
    return (
        "Continue the adventure from the selected choice only.\n\n"
        f"Previous story:\n{game_state.current_story}\n\n"
        f"{game_state.player.get_status()}\n"
        f"{event_text}"
        f"Chosen option: {choice.strip().upper()}\n\n"
        "Write the next scene and exactly three new choices."
    )

