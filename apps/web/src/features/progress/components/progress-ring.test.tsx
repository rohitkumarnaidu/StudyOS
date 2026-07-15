import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { ProgressRing } from "@/features/progress/components/progress-ring";

describe("ProgressRing", () => {
  it("renders percentage text", () => {
    render(<ProgressRing progress={75} />);
    expect(screen.getByText("75%")).toBeTruthy();
  });

  it("clamps negative progress to 0", () => {
    render(<ProgressRing progress={-10} />);
    expect(screen.getByText("0%")).toBeTruthy();
  });

  it("clamps progress over 100 to 100", () => {
    render(<ProgressRing progress={150} />);
    expect(screen.getByText("100%")).toBeTruthy();
  });

  it("shows label when provided", () => {
    render(<ProgressRing progress={50} label="Chapter 1" />);
    expect(screen.getByText("Chapter 1")).toBeTruthy();
  });

  it("hides label when showLabel is false", () => {
    render(<ProgressRing progress={50} label="Hidden" showLabel={false} />);
    expect(screen.queryByText("Hidden")).toBeNull();
  });

  it("applies custom className", () => {
    const { container } = render(<ProgressRing progress={30} className="test-class" />);
    expect(container.firstChild).toHaveClass("test-class");
  });

  it("uses emerald color for 100% progress", () => {
    const { container } = render(<ProgressRing progress={100} />);
    const circles = container.querySelectorAll("circle");
    expect(circles[1]).toHaveClass("text-emerald-500");
  });

  it("uses amber color for 50-99% progress", () => {
    const { container } = render(<ProgressRing progress={75} />);
    const circles = container.querySelectorAll("circle");
    expect(circles[1]).toHaveClass("text-amber-500");
  });

  it("uses blue color for <50% progress", () => {
    const { container } = render(<ProgressRing progress={25} />);
    const circles = container.querySelectorAll("circle");
    expect(circles[1]).toHaveClass("text-blue-500");
  });

  it("uses default size of 80", () => {
    const { container } = render(<ProgressRing progress={50} />);
    const wrapper = container.querySelector(".relative");
    expect(wrapper).toHaveStyle({ width: "80px", height: "80px" });
  });

  it("respects custom size", () => {
    const { container } = render(<ProgressRing progress={50} size={120} />);
    const wrapper = container.querySelector(".relative");
    expect(wrapper).toHaveStyle({ width: "120px", height: "120px" });
  });
});
