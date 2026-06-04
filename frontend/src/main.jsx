import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { Heart, Package, Play, Save, ScrollText, Sparkles, Wand2 } from "lucide-react";
import dungeonArt from "./assets/dungeon.svg";
import "./styles.css";

const API_URL = "http://127.0.0.1:5000";
const classes = ["Warrior", "Mage", "Rogue"];

function App() {
  const [name, setName] = useState("");
  const [characterClass, setCharacterClass] = useState("Warrior");
  const [game, setGame] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function callApi(path, options = {}) {
    setLoading(true);
    setMessage("");
    try {
      const response = await fetch(`${API_URL}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Something went wrong.");
      }
      return data;
    } catch (error) {
      setMessage(error.message);
      return null;
    } finally {
      setLoading(false);
    }
  }

  async function startGame(event) {
    event.preventDefault();
    const data = await callApi("/start-game", {
      method: "POST",
      body: JSON.stringify({ name, character_class: characterClass }),
    });
    if (data) setGame(data);
  }

  async function choose(choice) {
    const data = await callApi("/choose", {
      method: "POST",
      body: JSON.stringify({ choice }),
    });
    if (data) setGame(data);
  }

  async function loadGame() {
    const data = await callApi("/load");
    if (data) setGame(data);
  }

  async function saveGame() {
    const data = await callApi("/save", { method: "POST" });
    if (data) setMessage(data.message);
  }

  async function usePotion() {
    const data = await callApi("/use-potion", { method: "POST" });
    if (data) {
      setGame(data);
      setMessage(data.message);
    }
  }

  const inventory = game?.player?.inventory || [];

  return (
    <main className="app-shell">
      <section className="hero-panel" aria-label="AI Quest Master">
        <img src={dungeonArt} alt="" className="hero-art" />
        <div className="hero-copy">
          <p className="eyebrow">Local Ollama RPG</p>
          <h1>AI Quest Master</h1>
          <p>Choose a class, read the scene, and continue only through A, B, or C.</p>
        </div>
      </section>

      <section className="game-layout">
        <aside className="control-panel">
          <form onSubmit={startGame} className="new-game-form">
            <label>
              Character name
              <input
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Arden"
                maxLength={24}
              />
            </label>

            <div className="class-picker" aria-label="Choose a class">
              {classes.map((option) => (
                <button
                  type="button"
                  key={option}
                  className={characterClass === option ? "selected" : ""}
                  onClick={() => setCharacterClass(option)}
                >
                  {option}
                </button>
              ))}
            </div>

            <button className="primary-action" type="submit" disabled={loading}>
              <Play size={18} />
              Start Game
            </button>
          </form>

          <div className="utility-actions">
            <button onClick={loadGame} disabled={loading}>
              <ScrollText size={18} />
              Load
            </button>
            <button onClick={saveGame} disabled={loading || !game}>
              <Save size={18} />
              Save
            </button>
            <button onClick={usePotion} disabled={loading || !game}>
              <Wand2 size={18} />
              Potion
            </button>
          </div>

          {game && (
            <div className="status-panel">
              <div>
                <span>{game.player.name}</span>
                <strong>{game.player.character_class}</strong>
              </div>
              <div>
                <span><Heart size={16} /> Health</span>
                <strong>{game.player.health}</strong>
              </div>
              <div>
                <span><Package size={16} /> Inventory</span>
                <ul>
                  {inventory.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </aside>

        <section className="story-panel">
          <div className="story-header">
            <span><Sparkles size={18} /> Turn {game?.turn_count ?? 0}</span>
            {loading && <span className="loading">Thinking...</span>}
          </div>

          <article className="story-text">
            {game ? game.current_story : "Start a new game or load a saved quest."}
          </article>

          {game?.last_event && <p className="event-text">{game.last_event}</p>}
          {message && <p className="message-text">{message}</p>}

          <div className="choice-row" aria-label="Story choices">
            {["A", "B", "C"].map((choice) => (
              <button
                key={choice}
                onClick={() => choose(choice)}
                disabled={loading || !game || game.game_over}
              >
                {choice}
              </button>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);

