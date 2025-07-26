import { create } from "zustand";
import { toast } from "sonner"; 

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
  logout: () => void;
  attemptLogin: (user: AuthUser) => boolean;
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
  },
  
  logout: () => {
    set({ authUser: null });
    localStorage.removeItem("authUser");
    toast.success("Logged out successfully");
  },

  attemptLogin: (newUser: AuthUser): boolean => {
    // No restriction on existing user - proceed with login
    set({ authUser: newUser });
    localStorage.setItem("authUser", JSON.stringify(newUser));
    toast.success(`Welcome, ${newUser.email}!`);
    return true;
  },
}));

// Add cross-tab synchronization
if (typeof window !== 'undefined') {
  // Listen for localStorage changes from other tabs
  window.addEventListener('storage', (e) => {
    if (e.key === 'authUser') {
      const newUser = e.newValue ? JSON.parse(e.newValue) : null;
      
      // Update store state when localStorage changes from another tab
      useAuthStore.setState({ authUser: newUser });
      
      if (!newUser) {
        console.log("User logged out from another tab");
      } else {
        console.log("User logged in from another tab:", newUser.email);
      }
    }
  });

  // Sync state when tab becomes active
  window.addEventListener('focus', () => {
    const currentStoredUser = getInitialAuthUser();
    const currentStoreUser = useAuthStore.getState().authUser;
    
    // Sync if there's a difference
    if (JSON.stringify(currentStoredUser) !== JSON.stringify(currentStoreUser)) {
      useAuthStore.setState({ authUser: currentStoredUser });
      console.log("Synced state on focus:", currentStoredUser);
    }
  });
}