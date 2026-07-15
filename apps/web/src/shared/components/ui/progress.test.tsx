import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";
import { createRef } from "react";

import { Progress } from "./progress";

afterEach(() => {
  cleanup();
});

describe("Progress", () => {
  it("renders progress bar", () => {
    render(<Progress value={50} data-testid="progress" />);
    const progress = screen.getByTestId("progress");
    expect(progress).toBeTruthy();
    expect(progress).toHaveAttribute("role", "progressbar");
  });

  it("applies base styling", () => {
    render(<Progress value={50} data-testid="progress" />);
    const progress = screen.getByTestId("progress");
    expect(progress).toHaveClass("relative", "h-4", "w-full", "overflow-hidden", "rounded-full");
  });

  it("applies custom className", () => {
    render(<Progress value={50} className="custom-class" data-testid="progress" />);
    expect(screen.getByTestId("progress")).toHaveClass("custom-class");
  });

  it("renders with zero value", () => {
    render(<Progress value={0} data-testid="progress" />);
    const progress = screen.getByTestId("progress");
    expect(progress).toBeTruthy();
  });

  it("renders with 100 value", () => {
    render(<Progress value={100} data-testid="progress" />);
    const progress = screen.getByTestId("progress");
    expect(progress).toBeTruthy();
  });

  it("renders with undefined value", () => {
    render(<Progress data-testid="progress" />);
    const progress = screen.getByTestId("progress");
    expect(progress).toBeTruthy();
  });

  it("forwards ref correctly", () => {
    const ref = createRef<HTMLDivElement>();
    render(<Progress ref={ref} value={50} />);
    expect(ref.current).toBeTruthy();
  });
});
