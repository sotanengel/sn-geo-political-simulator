import { getHealthStatus } from "@/lib/health";

describe("health", () => {
  it("returns ok status", () => {
    expect(getHealthStatus()).toEqual({ status: "ok" });
  });
});
