import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";

import { StudyHeatmap } from "./study-heatmap";

afterEach(() => {
  cleanup();
});

describe("StudyHeatmap", () => {
  it("renders header", () => {
    render(
      <StudyHeatmap
        data={[
          { date: "2026-01-01", count: 5 },
          { date: "2026-01-02", count: 3 },
        ]}
      />
    );
    expect(screen.getByText("Study Activity")).toBeTruthy();
  });

  it("returns null for empty data", () => {
    const { container } = render(<StudyHeatmap data={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders legend with Less/More labels", () => {
    render(
      <StudyHeatmap
        data={[{ date: "2026-01-01", count: 1 }]}
      />
    );
    expect(screen.getByText("Less")).toBeTruthy();
    expect(screen.getByText("More")).toBeTruthy();
  });

  it("renders with single day", () => {
    render(
      <StudyHeatmap
        data={[{ date: "2026-01-01", count: 5 }]}
      />
    );
    expect(screen.getByText("Study Activity")).toBeTruthy();
  });

  it("renders with multiple days", () => {
    const data = Array.from({ length: 30 }, (_, i) => ({
      date: `2026-01-${String(i + 1).padStart(2, "0")}`,
      count: Math.floor(Math.random() * 10),
    }));
    render(<StudyHeatmap data={data} />);
    expect(screen.getByText("Study Activity")).toBeTruthy();
  });

  it("handles days with zero activity", () => {
    render(
      <StudyHeatmap
        data={[
          { date: "2026-01-01", count: 0 },
          { date: "2026-01-02", count: 5 },
        ]}
      />
    );
    expect(screen.getByText("Study Activity")).toBeTruthy();
  });
});
