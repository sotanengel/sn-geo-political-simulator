import { render, screen } from "@testing-library/react";
import Dashboard from "@/components/Dashboard";

const nations = [
  {
    id: "nation_0",
    name: "Nation-nation_0",
    category: "ISLAND",
    territory_size: 10,
    resources: { FOOD: 100, FUEL: 50, ORE: 20, TECH: 5, GOLD: 5 },
    is_extinct: false,
    controller: "HUMAN",
  },
];

describe("Dashboard", () => {
  it("renders turn info", () => {
    render(
      <Dashboard
        nations={nations}
        selectedNationId="nation_0"
        onSelectNation={() => {}}
        onPass={() => {}}
        turn={1}
        maxTurns={50}
      />
    );
    expect(screen.getByText(/ターン 1/)).toBeInTheDocument();
  });
});
