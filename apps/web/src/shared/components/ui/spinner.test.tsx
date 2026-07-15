import { render, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";

import { Spinner } from "./spinner";

afterEach(() => {
  cleanup();
});

describe("Spinner", () => {
  it("renders a spinner", () => {
    render(<Spinner />);
    const svg = document.querySelector("svg");
    expect(svg).toBeTruthy();
    expect(svg).toHaveClass("animate-spin");
  });

  it("applies default size (md)", () => {
    render(<Spinner />);
    const svg = document.querySelector("svg");
    expect(svg).toHaveClass("h-6 w-6");
  });

  it("supports small size", () => {
    render(<Spinner size="sm" />);
    const svg = document.querySelector("svg");
    expect(svg).toHaveClass("h-4 w-4");
  });

  it("supports large size", () => {
    render(<Spinner size="lg" />);
    const svg = document.querySelector("svg");
    expect(svg).toHaveClass("h-8 w-8");
  });

  it("has animate-spin class", () => {
    render(<Spinner />);
    const svg = document.querySelector("svg");
    expect(svg).toHaveClass("animate-spin");
  });

  it("applies custom className", () => {
    render(<Spinner className="custom-class" />);
    const container = document.querySelector(".flex.items-center.justify-center");
    expect(container).toHaveClass("custom-class");
  });

  it("spreads additional props", () => {
    render(<Spinner aria-label="Loading" />);
    const container = document.querySelector(".flex.items-center.justify-center");
    expect(container).toHaveAttribute("aria-label", "Loading");
  });
});
