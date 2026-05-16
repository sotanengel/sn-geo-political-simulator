"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Sphere } from "@react-three/drei";
import { cellToLatLng } from "h3-js";
import { useMemo } from "react";
import type { MapCell, NationView } from "@/lib/api";
import { latLngToVector3, nationColor } from "@/lib/mapColors";

interface GlobeMapProps {
  nations: NationView[];
  cells: MapCell[];
}

const TERRAIN_COLOR: Record<string, string> = {
  LAND: "#4a7c59",
  SHALLOW_SEA: "#2a4d6e",
  DEEP_SEA: "#0d1b2a",
};

function TerritoryDots({
  nations,
  cells,
}: {
  nations: NationView[];
  cells: MapCell[];
}) {
  const nationIndex = useMemo(() => {
    const map = new Map<string, number>();
    nations.forEach((n, i) => map.set(n.id, i));
    return map;
  }, [nations]);

  const dots = useMemo(() => {
    return cells.map((cell) => {
      const [lat, lng] = cellToLatLng(cell.h3);
      const idx = cell.owner_id ? nationIndex.get(cell.owner_id) : undefined;
      const color =
        idx !== undefined
          ? nationColor(idx)
          : TERRAIN_COLOR[cell.terrain] ?? "#333333";
      const [x, y, z] = latLngToVector3(lat, lng, 2.02);
      return { key: cell.h3, position: [x, y, z] as [number, number, number], color };
    });
  }, [cells, nationIndex]);

  return (
    <>
      {dots.map((d) => (
        <mesh key={d.key} position={d.position}>
          <sphereGeometry args={[0.018, 6, 6]} />
          <meshStandardMaterial color={d.color} />
        </mesh>
      ))}
    </>
  );
}

export default function GlobeMap({ nations, cells }: GlobeMapProps) {
  return (
    <div className="h-[480px] w-full rounded-lg border border-gray-700 bg-black">
      <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 5, 5]} intensity={1} />
        <Sphere args={[2, 64, 64]}>
          <meshStandardMaterial color="#1a1a2e" wireframe={false} />
        </Sphere>
        <TerritoryDots nations={nations} cells={cells} />
        <OrbitControls enablePan={false} minDistance={3} maxDistance={8} />
      </Canvas>
    </div>
  );
}
