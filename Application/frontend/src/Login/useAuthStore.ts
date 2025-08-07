import { create } from "zustand";
import { toast } from "sonner"; 
import { addSessionLog } from "./sessionLogger";
import axios from "axios"


export interface AuthUser {
  email: string;
  message: string;
  permission: number;
  role: string;
  time: string;
  user_id: number;
}

interface AuthStore {
  error: string | null;
  authUser: AuthUser | null;
  setAuthUser: (user: AuthUser) => void;
  logout: () => void;
  attemptLogin: (user: AuthUser) => Promise<boolean>;
  resetInactivityTimer: () => void;
  editUser: ({ user_id, time }: { user_id: number; time: string }) => Promise<void>;
}

const now = new Date().toISOString();
const INACTIVITY_TIMEOUT = 3 * 60 * 60 * 1000; // 3 hours in milliseconds
const WARNING_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds
let inactivityTimer: NodeJS.Timeout | null = null;
let warningTimer: NodeJS.Timeout | null = null;

const getInitialAuthUser = (): AuthUser | null => {
  try {
    const user = sessionStorage.getItem("authUser");
    return user ? JSON.parse(user) : null;
  } catch {
    return null;
  }
};

export const useAuthStore = create<AuthStore>((set, get) => ({
  error: null,
  authUser: getInitialAuthUser(),
  editUser: async ({ user_id, time }: { user_id: number; time: string }) => {
    try {
      const payload = {
        user_id,
        time,
      };

      console.log("Editing user with payload:", payload);
      const res = await axios.patch(
        `http://localhost:8000/api/useraccounts/${payload.user_id}/`,
        payload
      );
      console.log("user edit response:", res)
      if (res.status !== 200) throw new Error("Failed to update user");
    } catch (err) {
      // Fallback: update dummy data locally
      set({error: "Failed to update user on server."});
    }
  },
  setAuthUser: (user) => {
    set({ authUser: user });
    sessionStorage.setItem("authUser", JSON.stringify(user));
  },
  
  logout: () => {
    addSessionLog({
      user_id: get().authUser?.user_id || 0,
      email: get().authUser?.email || "",
      action: "logout",
      timestamp: now
    });
    set({ authUser: null });
    sessionStorage.removeItem("authUser");
    toast.success("Logged out successfully");
  },

  attemptLogin: async (newUser: AuthUser): Promise<boolean> => {
  const currentStoredUser = getInitialAuthUser();
  const currentStoreUser = get().authUser;
  const existingUser = currentStoredUser || currentStoreUser;

  const now = new Date().toISOString();
  if (existingUser) {

    if (existingUser.user_id === newUser.user_id && existingUser.email === newUser.email) {
      set({ authUser: newUser });
      sessionStorage.setItem("authUser", JSON.stringify(newUser)); 
      toast.success(`Welcome back, ${newUser.email}!`);

      // Update lastActive
       await get().editUser({ user_id: newUser.user_id, time: now });

      addSessionLog({
        user_id: newUser.user_id,
        email: newUser.email,
        action: "login",
        timestamp: now,
      });
      return true;
    }

    toast.error(`Another user is already logged in. Please logout first.`);
    return false;
  }

  set({ authUser: newUser });
  sessionStorage.setItem("authUser", JSON.stringify(newUser)); 
  toast.success(`Welcome, ${newUser.email}!`);

 await get().editUser({ user_id: newUser.user_id, time: now });

  addSessionLog({
    user_id: newUser.user_id,
    email: newUser.email,
    action: "login",
    timestamp: now,
  });
  return true;
},

  resetInactivityTimer: () => {
    if (inactivityTimer) clearTimeout(inactivityTimer);
    if (warningTimer) clearTimeout(warningTimer);

    inactivityTimer = setTimeout(() => {
      warningTimer = setTimeout(() => {
        get().logout();
        addSessionLog({
          user_id: get().authUser?.user_id || 0,
          email: get().authUser?.email || "",
          action: "logout",
          timestamp: now
        });
        toast.error("You have been logged out due to inactivity.");
      }, WARNING_DURATION);

      toast.warning("You will be logged out in 5 minutes due to inactivity.");
    }, INACTIVITY_TIMEOUT);
  },
}));

// Add cross-tab synchronization
if (typeof window !== 'undefined') {

  // Sync state when tab becomes active
  window.addEventListener('focus', () => {
    const currentStoredUser = getInitialAuthUser();
    const currentStoreUser = useAuthStore.getState().authUser;
    
    // Sync if there's a difference
    if (JSON.stringify(currentStoredUser) !== JSON.stringify(currentStoreUser)) {
      useAuthStore.setState({ authUser: currentStoredUser });
    }
  });
  window.addEventListener("mousemove", useAuthStore.getState().resetInactivityTimer);
  window.addEventListener("keydown", useAuthStore.getState().resetInactivityTimer);
  window.addEventListener("click", useAuthStore.getState().resetInactivityTimer);
}