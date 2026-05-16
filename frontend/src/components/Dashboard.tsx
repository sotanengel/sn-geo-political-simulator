"use client";

import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ActionPayload, MapCell, NationView } from "@/lib/api";

interface DashboardProps {
  nations: NationView[];
  cells: MapCell[];
  selectedNationId: string | null;
  onSelectNation: (id: string) => void;
  onPass: () => void;
  onAction: (action: Omit<ActionPayload, "nation_id">) => void;
  turn: number;
  maxTurns: number;
  gameOver: boolean;
  winners: string[];
  pendingActions: Record<string, boolean>;
}

export default function Dashboard({
  nations,
  cells,
  selectedNationId,
  onSelectNation,
  onPass,
  onAction,
  turn,
  maxTurns,
  gameOver,
  winners,
  pendingActions,
}: DashboardProps) {
  const [targetCell, setTargetCell] = useState("");
  const [sourceCell, setSourceCell] = useState("");
  const [units, setUnits] = useState(1);

  const selected = nations.find((n) => n.id === selectedNationId);
  const ownedCells = useMemo(() => {
    if (!selectedNationId) return [];
    return cells.filter((c) => c.owner_id === selectedNationId).map((c) => c.h3);
  }, [cells, selectedNationId]);

  const chartData = nations.map((n) => ({
    name: n.id.replace("nation_", "N"),
    territory: n.territory_size,
  }));

  const awaiting = selectedNationId
    ? pendingActions[selectedNationId] === true
    : false;

  return (
    <div className="flex flex-col gap-4">
      <div className="rounded-lg border border-gray-700 p-4">
        <h2 className="text-lg font-semibold">
          ターン {turn} / {maxTurns}
        </h2>
        {gameOver && (
          <p className="mt-1 text-sm text-amber-400">
            ゲーム終了 — 勝者: {winners.join(", ") || "なし"}
          </p>
        )}
        {awaiting && !gameOver && (
          <p className="mt-1 text-xs text-yellow-500">この国の行動待ち</p>
        )}
      </div>

      <div className="rounded-lg border border-gray-700 p-4">
        <label className="text-sm text-gray-400">国家を選択</label>
        <select
          className="mt-1 w-full rounded bg-gray-900 p-2"
          value={selectedNationId ?? ""}
          onChange={(e) => onSelectNation(e.target.value)}
        >
          <option value="">—</option>
          {nations.map((n) => (
            <option key={n.id} value={n.id}>
              {n.name} ({n.category})
            </option>
          ))}
        </select>
      </div>

      {selected && (
        <div className="rounded-lg border border-gray-700 p-4 text-sm">
          <h3 className="font-medium">{selected.name}</h3>
          <ul className="mt-2 space-y-1">
            {Object.entries(selected.resources).map(([k, v]) => (
              <li key={k}>
                {k}: {v}
              </li>
            ))}
          </ul>

          <div className="mt-4 space-y-2">
            <label className="text-xs text-gray-400">自国セル（MOVE/INVADE 元）</label>
            <select
              className="w-full rounded bg-gray-900 p-2 text-xs"
              value={sourceCell}
              onChange={(e) => setSourceCell(e.target.value)}
            >
              <option value="">—</option>
              {ownedCells.map((h3) => (
                <option key={h3} value={h3}>
                  {h3.slice(-8)}
                </option>
              ))}
            </select>
            <label className="text-xs text-gray-400">対象セル</label>
            <input
              className="w-full rounded bg-gray-900 p-2 text-xs"
              value={targetCell}
              onChange={(e) => setTargetCell(e.target.value)}
              placeholder="H3 index"
            />
            <label className="text-xs text-gray-400">ユニット数</label>
            <input
              type="number"
              min={1}
              className="w-full rounded bg-gray-900 p-2 text-xs"
              value={units}
              onChange={(e) => setUnits(Number(e.target.value))}
            />
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              className="rounded bg-blue-600 px-3 py-1 text-xs hover:bg-blue-500"
              onClick={onPass}
              disabled={selected.is_extinct || gameOver}
            >
              PASS
            </button>
            <button
              type="button"
              className="rounded bg-indigo-600 px-3 py-1 text-xs hover:bg-indigo-500"
              disabled={!sourceCell || !targetCell || gameOver}
              onClick={() =>
                onAction({
                  action_type: "MOVE",
                  source_cell: sourceCell,
                  target_cell: targetCell,
                  units,
                })
              }
            >
              MOVE
            </button>
            <button
              type="button"
              className="rounded bg-red-700 px-3 py-1 text-xs hover:bg-red-600"
              disabled={!sourceCell || !targetCell || gameOver}
              onClick={() =>
                onAction({
                  action_type: "INVADE",
                  source_cell: sourceCell,
                  target_cell: targetCell,
                  units,
                })
              }
            >
              INVADE
            </button>
          </div>
        </div>
      )}

      <div className="h-48 rounded-lg border border-gray-700 p-2">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="name" stroke="#888" />
            <YAxis stroke="#888" />
            <Tooltip />
            <Bar dataKey="territory" fill="#4363d8" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
