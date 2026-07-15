import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";

import { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent } from "./card";

afterEach(() => {
  cleanup();
});

describe("Card", () => {
  it("renders card container", () => {
    render(<Card data-testid="card">Card content</Card>);
    const card = screen.getByTestId("card");
    expect(card).toBeTruthy();
    expect(card).toHaveClass("rounded-lg", "border", "bg-card");
  });

  it("applies custom className", () => {
    render(<Card className="custom-class" data-testid="card">Custom</Card>);
    expect(screen.getByTestId("card")).toHaveClass("custom-class");
  });
});

describe("CardHeader", () => {
  it("renders header section", () => {
    render(<CardHeader data-testid="header">Header</CardHeader>);
    const header = screen.getByTestId("header");
    expect(header).toHaveClass("flex", "flex-col", "space-y-1.5", "p-6");
  });
});

describe("CardTitle", () => {
  it("renders as h3 element", () => {
    render(<CardTitle>Card Title</CardTitle>);
    const title = screen.getByText("Card Title");
    expect(title.tagName).toBe("H3");
    expect(title).toHaveClass("text-2xl", "font-semibold");
  });
});

describe("CardDescription", () => {
  it("renders description text", () => {
    render(<CardDescription>Card description</CardDescription>);
    const desc = screen.getByText("Card description");
    expect(desc.tagName).toBe("P");
    expect(desc).toHaveClass("text-sm", "text-muted-foreground");
  });
});

describe("CardContent", () => {
  it("renders content section", () => {
    render(<CardContent data-testid="content">Content</CardContent>);
    const content = screen.getByTestId("content");
    expect(content).toHaveClass("p-6", "pt-0");
  });
});

describe("CardFooter", () => {
  it("renders footer section", () => {
    render(<CardFooter data-testid="footer">Footer</CardFooter>);
    const footer = screen.getByTestId("footer");
    expect(footer).toHaveClass("flex", "items-center", "p-6");
  });
});

describe("Card Composition", () => {
  it("renders complete card structure", () => {
    render(
      <Card data-testid="card">
        <CardHeader>
          <CardTitle>Test Card</CardTitle>
          <CardDescription>Test description</CardDescription>
        </CardHeader>
        <CardContent>Test content</CardContent>
        <CardFooter>Test footer</CardFooter>
      </Card>
    );

    expect(screen.getByTestId("card")).toBeTruthy();
    expect(screen.getByText("Test Card")).toBeTruthy();
    expect(screen.getByText("Test description")).toBeTruthy();
    expect(screen.getByText("Test content")).toBeTruthy();
    expect(screen.getByText("Test footer")).toBeTruthy();
  });
});
