"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Sphere } from "@react-three/drei";
import { cellToLatLng, gridDisk } from "h3-js";
import { useMemo } from "react";
import type { NationView } from "@/lib/api";
import { latLngToVector3, nationColor } from "@/lib/mapColors";

interface GlobeMapProps {
  nations: NationView[];
}

function TerritoryDots({ nations }: { nations: NationView[] }) {
  const dots = useMemo(() => {
    const center = "81283ffffffffff";
    const cells = gridDisk(center, 2);
    return cells.map((cell, i) => {
      const [lat, lng] = cellToLatLng(cell);
      const nationIdx = i % Math.max(nations.length, 1);
      const color = nationColor(nationIdx);
      const [x, y, z] = latLngToVector3(lat, lng, 2.02);
      return { key: cell, position: [x, y, z] as [number, number, number], color };
    });
  }, [nations]);

  return (
    <>
      {dots.map((d) => (
        <mesh key={d.key} position={d.position}>
          <sphereGeometry args={[0.02, 6, 6]} />
          <meshStandardMaterial color={d.color} />
        </mesh>
      ))}
    </>
  );
}

export default function GlobeMap({ nations }: GlobeMapProps) {
  return (
    <div className="h-[480px] w-full rounded-lg border border-gray-700 bg-black">
      <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 5, 5]} intensity={1} />
        <Sphere args={[2, 64, 64]}>
          <meshStandardMaterial color="#1a1a2e" wireframe={false} />
        </Sphere>
        <TerritoryDots nations={nations} />
        <OrbitControls enablePan={false} minDistance={3} maxDistance={8} />
      </Canvas>
    </div>
  );
}
