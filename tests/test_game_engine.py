import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from database import load_game, save_game
from ai_service import normalize_choice_labels
from game_engine import create_player, is_valid_choice, use_health_potion
from models import GameState


class GameEngineTests(unittest.TestCase):
    def test_player_classes_have_expected_stats(self):
        warrior = create_player("Mira", "Warrior")
        mage = create_player("Sol", "Mage")
        rogue = create_player("Nyx", "Rogue")

        self.assertEqual(warrior.health, 120)
        self.assertIn("shield", warrior.inventory)
        self.assertEqual(mage.health, 80)
        self.assertIn("spell book", mage.inventory)
        self.assertEqual(rogue.health, 100)
        self.assertIn("lockpick", rogue.inventory)

    def test_invalid_class_raises_error(self):
        with self.assertRaises(ValueError):
            create_player("Mira", "Paladin")

    def test_choice_validation_only_allows_abc(self):
        self.assertTrue(is_valid_choice("A"))
        self.assertTrue(is_valid_choice("b"))
        self.assertTrue(is_valid_choice(" c "))
        self.assertFalse(is_valid_choice("attack"))
        self.assertFalse(is_valid_choice("D"))

    def test_health_potion_restores_health_once(self):
        state = GameState(player=create_player("Mira", "Warrior"), current_story="Start")
        state.player.health = 70

        message = use_health_potion(state)

        self.assertIn("recover", message)
        self.assertEqual(state.player.health, 100)
        self.assertNotIn("health potion", state.player.inventory)

    def test_save_and_load_game_state(self):
        state = GameState(player=create_player("Mira", "Mage"), current_story="A tower waits.")
        state.turn_count = 3
        state.last_event = "A trap snapped shut."

        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "test_save.db"
            save_game(state, database_path)
            loaded = load_game(database_path)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.player.name, "Mira")
        self.assertEqual(loaded.player.character_class, "Mage")
        self.assertEqual(loaded.current_story, "A tower waits.")
        self.assertEqual(loaded.turn_count, 3)
        self.assertEqual(loaded.last_event, "A trap snapped shut.")

    def test_ai_choice_labels_are_normalized(self):
        story = "A) Left path\nB: Center path\nC- Right path"

        normalized = normalize_choice_labels(story)

        self.assertEqual(normalized, "A. Left path\nB. Center path\nC. Right path")


if __name__ == "__main__":
    unittest.main()
