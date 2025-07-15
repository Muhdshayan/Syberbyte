import { create } from "zustand";

export interface AuthUser {
  email: string;
  message: string;
  permission: number;
  role: string;
  time: string;
  user_id: number;
}

interface AuthStore {
    authUser: AuthUser | null;
    setAuthUser: (user: AuthUser) => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
    authUser: null,
    setAuthUser: (user) => {set({ authUser: user })
      console.log("Auth user set:", user);
    },
}))