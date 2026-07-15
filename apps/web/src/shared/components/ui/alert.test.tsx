import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";

import { Alert, AlertTitle, AlertDescription } from "./alert";

afterEach(() => {
  cleanup();
});

describe("Alert", () => {
  it("renders with default variant", () => {
    render(<Alert>Default alert</Alert>);
    const alert = screen.getByRole("alert");
    expect(alert).toBeTruthy();
    expect(alert).toHaveClass("bg-background");
  });

  it("has role=alert", () => {
    render(<Alert>Unique test alert 123</Alert>);
    expect(screen.getByText("Unique test alert 123")).toHaveAttribute("role", "alert");
  });

  it("applies custom className", () => {
    render(<Alert className="custom-class">Custom alert 456</Alert>);
    const alert = screen.getByText("Custom alert 456");
    expect(alert).toHaveClass("custom-class");
  });

  it("renders with destructive variant", () => {
    render(<Alert variant="destructive">Destructive alert 789</Alert>);
    const alert = screen.getByText("Destructive alert 789");
    expect(alert).toHaveClass("text-destructive");
  });

  it("renders with success variant", () => {
    render(<Alert variant="success">Success alert 101</Alert>);
    const alert = screen.getByText("Success alert 101");
    expect(alert).toHaveClass("text-green-700");
  });

  it("renders with warning variant", () => {
    render(<Alert variant="warning">Warning alert 202</Alert>);
    const alert = screen.getByText("Warning alert 202");
    expect(alert).toHaveClass("text-yellow-700");
  });

  it("renders with info variant", () => {
    render(<Alert variant="info">Info alert 303</Alert>);
    const alert = screen.getByText("Info alert 303");
    expect(alert).toHaveClass("text-blue-700");
  });

  it("forwards ref correctly", () => {
    const ref = { current: null };
    render(<Alert ref={ref}>Ref alert 404</Alert>);
    expect(ref.current).toBeTruthy();
  });
});

describe("AlertTitle", () => {
  it("renders as h5 element", () => {
    render(<AlertTitle>Unique Title 505</AlertTitle>);
    const title = screen.getByText("Unique Title 505");
    expect(title.tagName).toBe("H5");
  });

  it("applies custom className", () => {
    render(<AlertTitle className="custom-class">Unique Title 606</AlertTitle>);
    const title = screen.getByText("Unique Title 606");
    expect(title).toHaveClass("custom-class");
  });
});

describe("AlertDescription", () => {
  it("renders description text", () => {
    render(<AlertDescription>Unique Desc 707</AlertDescription>);
    expect(screen.getByText("Unique Desc 707")).toBeTruthy();
  });

  it("applies custom className", () => {
    render(<AlertDescription className="custom-class">Unique Desc 808</AlertDescription>);
    const desc = screen.getByText("Unique Desc 808");
    expect(desc).toHaveClass("custom-class");
  });
});
