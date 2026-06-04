from flask import Flask, jsonify, request
from flask_cors import CORS

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


app = Flask(__name__)
CORS(app)

initialize_database()
active_game: GameState | None = None


def game_to_response(game_state: GameState) -> dict:
    return {
        "player": game_state.player.to_dict(),
        "current_story": game_state.current_story,
        "turn_count": game_state.turn_count,
        "game_over": game_state.game_over,
        "last_event": game_state.last_event,
    }


@app.post("/start-game")
def start_game():
    global active_game
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    character_class = data.get("character_class", "").strip()

    try:
        player = create_player(name, character_class)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    story = generate_story(build_opening_prompt(player))
    active_game = GameState(player=player, current_story=story)
    save_game(active_game)
    return jsonify(game_to_response(active_game))


@app.post("/choose")
def choose():
    global active_game
    if active_game is None:
        active_game = load_game()

    if active_game is None:
        return jsonify({"error": "No active game. Start or load a game first."}), 400

    data = request.get_json() or {}
    choice = data.get("choice", "").strip().upper()
    if not is_valid_choice(choice):
        return jsonify({"error": "Invalid choice. Please enter A, B, or C."}), 400

    apply_random_health_event(active_game)
    if not active_game.game_over:
        prompt = build_choice_prompt(active_game, choice)
        active_game.current_story = generate_story(prompt)
        active_game.turn_count += 1

    save_game(active_game)
    return jsonify(game_to_response(active_game))


@app.get("/status")
def status():
    if active_game is None:
        saved_game = load_game()
        if saved_game is None:
            return jsonify({"error": "No active game found."}), 404
        return jsonify(game_to_response(saved_game))
    return jsonify(game_to_response(active_game))


@app.post("/use-potion")
def use_potion():
    global active_game
    if active_game is None:
        active_game = load_game()

    if active_game is None:
        return jsonify({"error": "No active game. Start or load a game first."}), 400

    message = use_health_potion(active_game)
    save_game(active_game)
    response = game_to_response(active_game)
    response["message"] = message
    return jsonify(response)


@app.post("/save")
def save():
    if active_game is None:
        return jsonify({"error": "No active game to save."}), 400
    save_game(active_game)
    return jsonify({"message": "Game saved.", "game": game_to_response(active_game)})


@app.get("/load")
def load():
    global active_game
    saved_game = load_game()
    if saved_game is None:
        return jsonify({"error": "No saved game found."}), 404

    active_game = saved_game
    return jsonify(game_to_response(active_game))


if __name__ == "__main__":
    app.run(debug=True, port=5000)

