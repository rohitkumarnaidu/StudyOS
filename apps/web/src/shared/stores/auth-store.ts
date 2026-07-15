import { create } from "zustand";

interface AuthState {
  isAuthenticated: boolean;
  user: { id: string; email: string | null; displayName: string | null } | null;
  roles: string[];
  setAuth: (auth: {
    isAuthenticated: boolean;
    user: { id: string; email: string | null; displayName: string | null } | null;
    roles: string[];
  }) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  roles: [],
  setAuth: (auth) => set(auth),
  clearAuth: () => set({ isAuthenticated: false, user: null, roles: [] }),
}));
