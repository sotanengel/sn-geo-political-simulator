import { latLngToVector3, nationColor } from "@/lib/mapColors";

describe("mapColors", () => {
  it("returns consistent nation colors", () => {
    expect(nationColor(0)).toBe(nationColor(0));
    expect(nationColor(1)).not.toBe(nationColor(0));
  });

  it("converts lat/lng to 3D vector on sphere", () => {
    const [x, y, z] = latLngToVector3(0, 0, 1);
    const dist = Math.sqrt(x * x + y * y + z * z);
    expect(dist).toBeCloseTo(1, 5);
  });
});
