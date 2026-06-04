import json
import os
import sqlite3
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> None:
        return None

from models import GameState


load_dotenv()

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent / os.getenv(
    "DATABASE_PATH", "game_saves.db"
)


def get_connection(database_path: Path = DEFAULT_DATABASE_PATH) -> sqlite3.Connection:
    return sqlite3.connect(database_path)


def initialize_database(database_path: Path = DEFAULT_DATABASE_PATH) -> None:
    connection = get_connection(database_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS saves (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                player_name TEXT NOT NULL,
                character_class TEXT NOT NULL,
                health INTEGER NOT NULL,
                inventory TEXT NOT NULL,
                current_story TEXT NOT NULL,
                turn_count INTEGER NOT NULL,
                game_over INTEGER NOT NULL,
                last_event TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def save_game(game_state: GameState, database_path: Path = DEFAULT_DATABASE_PATH) -> None:
    initialize_database(database_path)
    player = game_state.player
    connection = get_connection(database_path)
    try:
        connection.execute(
            """
            INSERT INTO saves (
                id, player_name, character_class, health, inventory,
                current_story, turn_count, game_over, last_event, updated_at
            )
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                player_name = excluded.player_name,
                character_class = excluded.character_class,
                health = excluded.health,
                inventory = excluded.inventory,
                current_story = excluded.current_story,
                turn_count = excluded.turn_count,
                game_over = excluded.game_over,
                last_event = excluded.last_event,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                player.name,
                player.character_class,
                player.health,
                json.dumps(player.inventory),
                game_state.current_story,
                game_state.turn_count,
                int(game_state.game_over),
                game_state.last_event,
            ),
        )
        connection.commit()
    finally:
        connection.close()


def load_game(database_path: Path = DEFAULT_DATABASE_PATH) -> GameState | None:
    initialize_database(database_path)
    connection = get_connection(database_path)
    try:
        connection.row_factory = sqlite3.Row
        row = connection.execute("SELECT * FROM saves WHERE id = 1").fetchone()
    finally:
        connection.close()

    if row is None:
        return None

    return GameState.from_dict(
        {
            "player": {
                "name": row["player_name"],
                "character_class": row["character_class"],
                "health": row["health"],
                "inventory": json.loads(row["inventory"]),
            },
            "current_story": row["current_story"],
            "turn_count": row["turn_count"],
            "game_over": bool(row["game_over"]),
            "last_event": row["last_event"],
        }
    )
