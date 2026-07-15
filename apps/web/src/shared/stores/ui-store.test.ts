import { describe, it, expect, beforeEach } from "vitest";

import { useUiStore } from "./ui-store";

describe("useUiStore", () => {
  beforeEach(() => {
    useUiStore.setState({
      sidebarOpen: true,
      theme: "system",
    });
  });

  it("has default state", () => {
    const state = useUiStore.getState();
    expect(state.sidebarOpen).toBe(true);
    expect(state.theme).toBe("system");
  });

  it("toggles sidebar", () => {
    useUiStore.getState().toggleSidebar();
    expect(useUiStore.getState().sidebarOpen).toBe(false);

    useUiStore.getState().toggleSidebar();
    expect(useUiStore.getState().sidebarOpen).toBe(true);
  });

  it("sets sidebar open", () => {
    useUiStore.getState().setSidebarOpen(false);
    expect(useUiStore.getState().sidebarOpen).toBe(false);

    useUiStore.getState().setSidebarOpen(true);
    expect(useUiStore.getState().sidebarOpen).toBe(true);
  });

  it("sets theme", () => {
    useUiStore.getState().setTheme("dark");
    expect(useUiStore.getState().theme).toBe("dark");

    useUiStore.getState().setTheme("light");
    expect(useUiStore.getState().theme).toBe("light");

    useUiStore.getState().setTheme("system");
    expect(useUiStore.getState().theme).toBe("system");
  });

  it("has all required actions", () => {
    const state = useUiStore.getState();
    expect(typeof state.setSidebarOpen).toBe("function");
    expect(typeof state.setTheme).toBe("function");
    expect(typeof state.toggleSidebar).toBe("function");
  });
});
