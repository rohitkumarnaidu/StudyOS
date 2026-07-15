import { render, screen, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, afterEach } from "vitest";

import { Input } from "./input";

afterEach(() => {
  cleanup();
});

describe("Input", () => {
  it("renders an input element", () => {
    render(<Input placeholder="Enter text unique-1" />);
    const input = screen.getByPlaceholderText("Enter text unique-1");
    expect(input).toBeTruthy();
    expect(input.tagName).toBe("INPUT");
  });

  it("applies custom className", () => {
    render(<Input className="custom-class-unique" />);
    const input = document.querySelector(".custom-class-unique");
    expect(input).toBeTruthy();
    expect(input?.tagName).toBe("INPUT");
  });

  it("supports different input types", () => {
    render(<Input type="password" />);
    const input = document.querySelector('input[type="password"]');
    expect(input).toBeTruthy();
  });

  it("supports disabled state", () => {
    render(<Input disabled />);
    const input = document.querySelector("input:disabled");
    expect(input).toBeTruthy();
  });

  it("forwards ref correctly", () => {
    const ref = vi.fn();
    render(<Input ref={ref} />);
    expect(ref).toHaveBeenCalled();
    expect(ref.mock.calls[0][0]).toBeTruthy();
  });

  it("handles value changes", async () => {
    const user = userEvent.setup();
    render(<Input placeholder="Type here unique-2" />);
    const input = screen.getByPlaceholderText("Type here unique-2");
    await user.type(input, "hello");
    expect(input).toHaveValue("hello");
  });

  it("spreads additional props", () => {
    render(<Input aria-label="Unique Email Address 3" autoComplete="email" />);
    const input = document.querySelector('input[aria-label="Unique Email Address 3"]');
    expect(input).toBeTruthy();
    expect(input).toHaveAttribute("autoComplete", "email");
  });
});
