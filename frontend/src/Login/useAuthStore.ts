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

const getInitialAuthUser = (): AuthUser | null => {
  try {
    const user = localStorage.getItem("authUser");
    return user ? JSON.parse(user) : null;
  } catch {
    return null;
  }
};

export const useAuthStore = create<AuthStore>((set) => ({
  authUser: getInitialAuthUser(),
  setAuthUser: (user) => {
    set({ authUser: user });
    localStorage.setItem("authUser", JSON.stringify(user));
    console.log("Auth user set:", user);
  },
}))