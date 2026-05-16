"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { NationView } from "@/lib/api";

interface DashboardProps {
  nations: NationView[];
  selectedNationId: string | null;
  onSelectNation: (id: string) => void;
  onPass: () => void;
  turn: number;
  maxTurns: number;
}

export default function Dashboard({
  nations,
  selectedNationId,
  onSelectNation,
  onPass,
  turn,
  maxTurns,
}: DashboardProps) {
  const selected = nations.find((n) => n.id === selectedNationId);
  const chartData = nations.map((n) => ({
    name: n.id.replace("nation_", "N"),
    territory: n.territory_size,
  }));

  return (
    <div className="flex flex-col gap-4">
      <div className="rounded-lg border border-gray-700 p-4">
        <h2 className="text-lg font-semibold">ターン {turn} / {maxTurns}</h2>
        <p className="text-sm text-gray-400">国家ダッシュボード</p>
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
          <button
            type="button"
            className="mt-4 rounded bg-blue-600 px-4 py-2 text-sm hover:bg-blue-500"
            onClick={onPass}
            disabled={selected.is_extinct}
          >
            PASS（何もしない）
          </button>
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
