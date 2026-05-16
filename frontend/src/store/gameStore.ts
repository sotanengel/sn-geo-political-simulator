import { create } from "zustand";
import type { GameState } from "@/lib/api";

interface GameStore {
  gameId: string | null;
  gameState: GameState | null;
  selectedNationId: string | null;
  log: string[];
  setGameId: (id: string | null) => void;
  setGameState: (state: GameState | null) => void;
  setSelectedNation: (id: string | null) => void;
  appendLog: (message: string) => void;
}

export const useGameStore = create<GameStore>((set) => ({
  gameId: null,
  gameState: null,
  selectedNationId: null,
  log: [],
  setGameId: (gameId) => set({ gameId }),
  setGameState: (gameState) => set({ gameState }),
  setSelectedNation: (selectedNationId) => set({ selectedNationId }),
  appendLog: (message) =>
    set((s) => ({ log: [...s.log.slice(-99), message] })),
}));
