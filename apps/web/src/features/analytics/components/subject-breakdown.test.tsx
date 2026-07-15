import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";

import { SubjectBreakdown } from "./subject-breakdown";

afterEach(() => {
  cleanup();
});

describe("SubjectBreakdown", () => {
  it("renders header", () => {
    render(
      <SubjectBreakdown
        data={[
          { name: "Physics", completed: 10, total: 20, percentage: 50 },
        ]}
      />
    );
    expect(screen.getByText("Subject Breakdown")).toBeTruthy();
  });

  it("renders subject names in legend", () => {
    render(
      <SubjectBreakdown
        data={[
          { name: "Physics", completed: 10, total: 20, percentage: 50 },
          { name: "Chemistry", completed: 8, total: 20, percentage: 40 },
        ]}
      />
    );
    expect(screen.getByText("Physics")).toBeTruthy();
    expect(screen.getByText("Chemistry")).toBeTruthy();
  });

  it("displays completion stats", () => {
    render(
      <SubjectBreakdown
        data={[
          { name: "Physics", completed: 10, total: 20, percentage: 50 },
        ]}
      />
    );
    expect(screen.getByText("10/20 (50%)")).toBeTruthy();
  });

  it("renders multiple subjects", () => {
    render(
      <SubjectBreakdown
        data={[
          { name: "Physics", completed: 10, total: 20, percentage: 50 },
          { name: "Chemistry", completed: 8, total: 20, percentage: 40 },
          { name: "Biology", completed: 15, total: 20, percentage: 75 },
        ]}
      />
    );
    expect(screen.getByText("Physics")).toBeTruthy();
    expect(screen.getByText("Chemistry")).toBeTruthy();
    expect(screen.getByText("Biology")).toBeTruthy();
  });

  it("renders with zero completion", () => {
    render(
      <SubjectBreakdown
        data={[
          { name: "Physics", completed: 0, total: 20, percentage: 0 },
        ]}
      />
    );
    expect(screen.getByText("0/20 (0%)")).toBeTruthy();
  });

  it("renders with 100% completion", () => {
    render(
      <SubjectBreakdown
        data={[
          { name: "Physics", completed: 20, total: 20, percentage: 100 },
        ]}
      />
    );
    expect(screen.getByText("20/20 (100%)")).toBeTruthy();
  });
});
