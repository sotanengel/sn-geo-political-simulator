import { useGameStore } from "@/store/gameStore";

describe("gameStore", () => {
  it("stores game id and log", () => {
    useGameStore.getState().setGameId("test-id");
    useGameStore.getState().appendLog("hello");
    expect(useGameStore.getState().gameId).toBe("test-id");
    expect(useGameStore.getState().log).toContain("hello");
  });
});
