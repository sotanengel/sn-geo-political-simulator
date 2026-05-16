"use client";

import dynamic from "next/dynamic";
import { useCallback, useState } from "react";
import { createGame, fetchGameState, submitPass } from "@/lib/api";
import { useSSE } from "@/hooks/useSSE";
import { useGameStore } from "@/store/gameStore";
import Dashboard from "@/components/Dashboard";

const GlobeMap = dynamic(() => import("@/components/GlobeMap"), { ssr: false });

export default function GameClient() {
  const [loading, setLoading] = useState(false);
  const gameId = useGameStore((s) => s.gameId);
  const gameState = useGameStore((s) => s.gameState);
  const selectedNationId = useGameStore((s) => s.selectedNationId);
  const log = useGameStore((s) => s.log);
  const setGameId = useGameStore((s) => s.setGameId);
  const setGameState = useGameStore((s) => s.setGameState);
  const setSelectedNation = useGameStore((s) => s.setSelectedNation);
  const appendLog = useGameStore((s) => s.appendLog);

  useSSE(gameId);

  const startGame = useCallback(async () => {
    setLoading(true);
    try {
      const { game_id } = await createGame(6, Date.now());
      const state = await fetchGameState(game_id);
      setGameId(game_id);
      setGameState(state);
      setSelectedNation(state.nations[0]?.id ?? null);
      appendLog(`Game ${game_id} started`);
    } catch (e) {
      appendLog(`Error: ${e}`);
    } finally {
      setLoading(false);
    }
  }, [setGameId, setGameState, setSelectedNation, appendLog]);

  const handlePass = useCallback(async () => {
    if (!gameId || !selectedNationId) return;
    try {
      const state = await submitPass(gameId, selectedNationId);
      setGameState(state);
      appendLog(`${selectedNationId} passed`);
    } catch (e) {
      appendLog(`Action error: ${e}`);
    }
  }, [gameId, selectedNationId, setGameState, appendLog]);

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">地政学戦略シミュレーション</h1>
        <button
          type="button"
          onClick={startGame}
          disabled={loading}
          className="rounded bg-emerald-600 px-4 py-2 text-sm hover:bg-emerald-500 disabled:opacity-50"
        >
          {loading ? "作成中…" : "新規ゲーム"}
        </button>
      </header>

      {gameState && (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <GlobeMap nations={gameState.nations} />
          </div>
          <Dashboard
            nations={gameState.nations}
            selectedNationId={selectedNationId}
            onSelectNation={setSelectedNation}
            onPass={handlePass}
            turn={gameState.turn}
            maxTurns={gameState.max_turns}
          />
        </div>
      )}

      <div className="rounded-lg border border-gray-700 p-4">
        <h2 className="mb-2 text-sm font-medium text-gray-400">ゲームログ</h2>
        <ul className="max-h-32 space-y-1 overflow-y-auto text-xs text-gray-300">
          {log.map((line, i) => (
            <li key={i}>{line}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
