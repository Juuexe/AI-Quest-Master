# AI Quest Master

AI Quest Master is a Python text RPG where Ollama runs the local dungeon master. The terminal version is complete first, and the same game engine is also exposed through a Flask API for the React web app.

## Features

- Local AI story generation with Ollama and `llama3.2`
- Strict story choices: the player continues with only `A`, `B`, or `C`
- Warrior, Mage, and Rogue classes with different health and inventories
- Player status, inventory display, and health potion use
- Simple random health events
- SQLite save/load
- Flask API routes for a full-stack version
- React frontend with clickable choices, save/load, status, and inventory

## Project Structure

```text
ROLE-PLAYING-GAME/
├── backend/
│   ├── ai_service.py
│   ├── api.py
│   ├── app.py
│   ├── database.py
│   ├── game_engine.py
│   └── models.py
├── frontend/
│   ├── src/
│   ├── index.html
│   └── package.json
├── tests/
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup

Install Ollama, then pull the local model:

```bash
ollama pull llama3.2
```

Create and activate a Python virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install Python packages:

```bash
python -m pip install -r requirements.txt
```

Optional: copy the environment example:

```bash
copy backend\.env.example backend\.env
```

## Run The Terminal Game

```bash
cd backend
python app.py
```

The story choice prompt accepts `A`, `B`, or `C`. Invalid story choices print:

```text
Invalid choice. Please enter A, B, or C.
```

The terminal version also supports `USE POTION` and `QUIT` as utility commands outside the AI story choices.

## Run The Flask API

In one terminal:

```bash
cd backend
python api.py
```

Routes:

- `POST /start-game`
- `POST /choose`
- `GET /status`
- `POST /use-potion`
- `POST /save`
- `GET /load`

## Run The React App

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, usually `http://127.0.0.1:5173`.

## Run Tests

```bash
python -m unittest discover tests
```

## Notes

messing around with codex and locally ran LLM 
