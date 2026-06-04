from ai_service import generate_story
from database import initialize_database, load_game, save_game
from game_engine import (
    apply_random_health_event,
    build_choice_prompt,
    build_opening_prompt,
    create_player,
    is_valid_choice,
    use_health_potion,
)
from models import GameState


def choose_class() -> str:
    while True:
        character_class = input("Choose a class (Warrior, Mage, Rogue): ").strip()
        try:
            create_player("Preview", character_class)
            return character_class
        except ValueError:
            print("Invalid class. Please choose Warrior, Mage, or Rogue.")


def start_new_game() -> GameState:
    name = input("Enter your character name: ").strip()
    character_class = choose_class()
    player = create_player(name, character_class)
    opening_story = generate_story(build_opening_prompt(player))
    return GameState(player=player, current_story=opening_story)


def choose_start_mode() -> GameState:
    initialize_database()
    print("AI Quest Master")
    print("1. New game")
    print("2. Load saved game")

    while True:
        mode = input("Choose 1 or 2: ").strip()
        if mode == "1":
            return start_new_game()
        if mode == "2":
            saved_game = load_game()
            if saved_game:
                print("Saved game loaded.")
                return saved_game
            print("No saved game found. Starting a new game.")
            return start_new_game()
        print("Invalid choice. Please enter 1 or 2.")


def print_game(game_state: GameState) -> None:
    print("\n" + "=" * 60)
    print(game_state.current_story)
    print("-" * 60)
    print(game_state.player.get_status())
    if game_state.last_event:
        print(f"Last event: {game_state.last_event}")
    print("=" * 60)


def run_game() -> None:
    game_state = choose_start_mode()

    while not game_state.game_over:
        print_game(game_state)
        print("Type A, B, or C to continue.")
        print("Type USE POTION to use a health potion, or QUIT to save and exit.")
        player_input = input("Your choice: ").strip().upper()

        if player_input == "QUIT":
            save_game(game_state)
            print("Game saved. Goodbye.")
            return

        if player_input == "USE POTION":
            print(use_health_potion(game_state))
            continue

        if not is_valid_choice(player_input):
            print("Invalid choice. Please enter A, B, or C.")
            continue

        apply_random_health_event(game_state)
        if game_state.game_over:
            break

        prompt = build_choice_prompt(game_state, player_input)
        game_state.current_story = generate_story(prompt)
        game_state.turn_count += 1
        save_game(game_state)

    print_game(game_state)
    save_game(game_state)
    print("Game over. Final state saved.")


if __name__ == "__main__":
    run_game()

