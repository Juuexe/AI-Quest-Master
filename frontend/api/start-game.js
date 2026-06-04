import { handleError, sendJson, startGame } from "./_game.js";

export default function handler(req, res) {
  if (req.method === "OPTIONS") return sendJson(res, 200, {});
  if (req.method !== "POST") return sendJson(res, 405, { error: "Method not allowed." });

  try {
    sendJson(res, 200, startGame(req.body || {}));
  } catch (error) {
    handleError(res, error);
  }
}

