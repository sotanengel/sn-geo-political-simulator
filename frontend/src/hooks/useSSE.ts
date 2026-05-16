"use client";

import { useEffect } from "react";
import { eventsUrl, fetchGameState } from "@/lib/api";
import { useGameStore } from "@/store/gameStore";

export function useSSE(gameId: string | null) {
  const setGameState = useGameStore((s) => s.setGameState);
  const appendLog = useGameStore((s) => s.appendLog);

  useEffect(() => {
    if (!gameId) return;

    const source = new EventSource(eventsUrl(gameId));

    source.onmessage = async (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.event === "state_updated") {
          const state = await fetchGameState(gameId);
          setGameState(state);
          appendLog(`Turn ${state.turn} resolved`);
        }
      } catch {
        /* ping or parse error */
      }
    };

    source.onerror = () => {
      appendLog("SSE connection error");
    };

    return () => source.close();
  }, [gameId, setGameState, appendLog]);
}
