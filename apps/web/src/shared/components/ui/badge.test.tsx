import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";

import { Badge, badgeVariants } from "./badge";

afterEach(() => {
  cleanup();
});

describe("Badge", () => {
  it("renders with default variant", () => {
    render(<Badge>Default Badge 1</Badge>);
    const badge = screen.getByText("Default Badge 1");
    expect(badge).toBeTruthy();
    expect(badge.tagName).toBe("DIV");
  });

  it("applies custom className", () => {
    render(<Badge className="custom-badge-class">Custom Badge 2</Badge>);
    const badge = screen.getByText("Custom Badge 2");
    expect(badge).toHaveClass("custom-badge-class");
  });

  it("renders with secondary variant", () => {
    render(<Badge variant="secondary">Secondary Badge 3</Badge>);
    const badge = screen.getByText("Secondary Badge 3");
    expect(badge).toHaveClass("bg-secondary");
  });

  it("renders with destructive variant", () => {
    render(<Badge variant="destructive">Destructive Badge 4</Badge>);
    const badge = screen.getByText("Destructive Badge 4");
    expect(badge).toHaveClass("bg-destructive");
  });

  it("renders with outline variant", () => {
    render(<Badge variant="outline">Outline Badge 5</Badge>);
    const badge = screen.getByText("Outline Badge 5");
    expect(badge).toHaveClass("text-foreground");
  });

  it("exports badgeVariants", () => {
    expect(badgeVariants).toBeDefined();
    expect(typeof badgeVariants).toBe("function");
  });

  it("spreads additional HTML props", () => {
    render(<Badge role="status">Status Badge 6</Badge>);
    const badge = screen.getByText("Status Badge 6");
    expect(badge).toHaveAttribute("role", "status");
  });
});
