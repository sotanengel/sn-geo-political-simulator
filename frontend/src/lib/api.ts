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

export interface MapCell {
  h3: string;
  owner_id: string | null;
  terrain: string;
}

export interface GameState {
  game_id: string;
  turn: number;
  max_turns: number;
  game_over: boolean;
  winners: string[];
  nations: NationView[];
  pending_actions: Record<string, boolean>;
  cells: MapCell[];
}

export type ActionType =
  | "PASS"
  | "MOVE"
  | "INVADE"
  | "TRADE_OFFER"
  | "TRADE_ACCEPT"
  | "TRADE_REJECT"
  | "GIFT";

export interface ActionPayload {
  nation_id: string;
  action_type: ActionType;
  source_cell?: string;
  target_cell?: string;
  units?: number;
  trade?: {
    to_nation: string;
    offer: Record<string, number>;
    request: Record<string, number>;
  };
  trade_offer_id?: string;
}

export async function createGame(
  numNations = 6,
  seed = 42,
  h3Resolution = 2
): Promise<{ game_id: string }> {
  const res = await fetch(`${API_URL}/api/v1/games`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      config: { num_nations: numNations, max_turns: 20, h3_resolution: h3Resolution },
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

export async function submitAction(
  gameId: string,
  action: ActionPayload
): Promise<GameState> {
  const res = await fetch(`${API_URL}/api/v1/games/${gameId}/actions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(action),
  });
  if (!res.ok) throw new Error("Failed to submit action");
  return res.json();
}

export async function submitPass(gameId: string, nationId: string): Promise<GameState> {
  return submitAction(gameId, { nation_id: nationId, action_type: "PASS" });
}

export function eventsUrl(gameId: string): string {
  return `${API_URL}/api/v1/games/${gameId}/events`;
}
