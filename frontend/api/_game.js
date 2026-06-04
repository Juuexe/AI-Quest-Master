const classData = {
  Warrior: {
    health: 120,
    inventory: ["sword", "shield", "health potion"],
  },
  Mage: {
    health: 80,
    inventory: ["staff", "mana potion", "spell book"],
  },
  Rogue: {
    health: 100,
    inventory: ["dagger", "lockpick", "smoke bomb"],
  },
};

const scenes = [
  {
    place: "moonlit ruin",
    threat: "a door carved with a watching eye",
    treasure: "a silver compass humming in your pack",
  },
  {
    place: "ash-dusted library",
    threat: "a whisper moving between the shelves",
    treasure: "a map inked in green fire",
  },
  {
    place: "frozen bridge",
    threat: "shadows gathering under the ice",
    treasure: "a warm rune stone pulsing in your palm",
  },
  {
    place: "underground garden",
    threat: "vines tightening around old statues",
    treasure: "a glass seed filled with starlight",
  },
];

function makePlayer(name, characterClass) {
  const cleanClass = classData[characterClass] ? characterClass : null;
  if (!cleanClass) {
    throw new Error("Invalid class. Please choose Warrior, Mage, or Rogue.");
  }

  return {
    name: name?.trim() || "Hero",
    character_class: cleanClass,
    health: classData[cleanClass].health,
    inventory: [...classData[cleanClass].inventory],
  };
}

function maxHealth(player) {
  return classData[player.character_class]?.health || 100;
}

function buildStory(game, choice = "") {
  const scene = scenes[game.turn_count % scenes.length];
  const choiceText = choice ? `After choosing ${choice}, ` : "";
  return `${choiceText}${game.player.name} enters the ${scene.place}. ${scene.threat} blocks the way, while ${scene.treasure} hints that this path is not ordinary.

A. Study the danger before moving closer.
B. Use your class training to press forward.
C. Search for a hidden route around the obstacle.`;
}

function applyEvent(game, choice) {
  const eventRoll = (game.turn_count + choice.charCodeAt(0)) % 4;
  if (eventRoll === 0) {
    const damage = 8 + game.turn_count;
    game.player.health = Math.max(0, game.player.health - damage);
    game.last_event = `A sudden trap triggers. You lose ${damage} health.`;
  } else if (eventRoll === 1) {
    const healing = 5;
    const before = game.player.health;
    game.player.health = Math.min(maxHealth(game.player), game.player.health + healing);
    game.last_event = `You find a brief safe moment and recover ${game.player.health - before} health.`;
  } else {
    game.last_event = "";
  }

  if (game.player.health <= 0) {
    game.game_over = true;
    game.last_event = "Your health has reached 0. Your quest ends here.";
  }
}

function startGame({ name, character_class }) {
  const player = makePlayer(name, character_class);
  const game = {
    player,
    current_story: "",
    turn_count: 0,
    game_over: false,
    last_event: "",
    demo_mode: true,
  };
  game.current_story = buildStory(game);
  return game;
}

function choose({ game, choice }) {
  if (!game) {
    throw new Error("No active game. Start or load a game first.");
  }

  const cleanChoice = String(choice || "").trim().toUpperCase();
  if (!["A", "B", "C"].includes(cleanChoice)) {
    throw new Error("Invalid choice. Please enter A, B, or C.");
  }

  const nextGame = structuredClone(game);
  applyEvent(nextGame, cleanChoice);
  if (!nextGame.game_over) {
    nextGame.turn_count += 1;
    nextGame.current_story = buildStory(nextGame, cleanChoice);
  }
  return nextGame;
}

function usePotion({ game }) {
  if (!game) {
    throw new Error("No active game. Start or load a game first.");
  }

  const nextGame = structuredClone(game);
  const potionIndex = nextGame.player.inventory.findIndex((item) => item.toLowerCase() === "health potion");
  if (potionIndex === -1) {
    nextGame.message = "You do not have a health potion.";
    return nextGame;
  }

  if (nextGame.player.health >= maxHealth(nextGame.player)) {
    nextGame.message = "Your health is already full.";
    return nextGame;
  }

  nextGame.player.inventory.splice(potionIndex, 1);
  const before = nextGame.player.health;
  nextGame.player.health = Math.min(maxHealth(nextGame.player), nextGame.player.health + 30);
  nextGame.message = `You use a health potion and recover ${nextGame.player.health - before} health.`;
  return nextGame;
}

function sendJson(res, status, data) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.status(status).json(data);
}

function handleError(res, error) {
  sendJson(res, 400, { error: error.message || "Something went wrong." });
}

module.exports = {
  choose,
  handleError,
  sendJson,
  startGame,
  usePotion,
};

