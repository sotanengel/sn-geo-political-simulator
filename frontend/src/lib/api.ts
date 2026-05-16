const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface NationView {
  id: string;
  name: string;
  category: string;
  territory_size: number;
  resources: Record<string, number>;
  is_extinct: boolean;
  controller: string;
}

export interface GameState {
  game_id: string;
  turn: number;
  max_turns: number;
  game_over: boolean;
  winners: string[];
  nations: NationView[];
  pending_actions: Record<string, boolean>;
}

export async function createGame(
  numNations = 6,
  seed = 42
): Promise<{ game_id: string }> {
  const res = await fetch(`${API_URL}/api/v1/games`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      config: { num_nations: numNations, max_turns: 20, h3_resolution: 1 },
      seed,
    }),
  });
  if (!res.ok) throw new Error("Failed to create game");
  return res.json();
}

export async function fetchGameState(gameId: string): Promise<GameState> {
  const res = await fetch(`${API_URL}/api/v1/games/${gameId}/state`);
  if (!res.ok) throw new Error("Failed to fetch game state");
  return res.json();
}

export async function submitPass(gameId: string, nationId: string): Promise<GameState> {
  const res = await fetch(`${API_URL}/api/v1/games/${gameId}/actions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nation_id: nationId, action_type: "PASS" }),
  });
  if (!res.ok) throw new Error("Failed to submit action");
  return res.json();
}

export function eventsUrl(gameId: string): string {
  return `${API_URL}/api/v1/games/${gameId}/events`;
}
