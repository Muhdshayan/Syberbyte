const dummyUsers: User[] = [
  {
    id: 1,
    name: "Alice Johnson",
    email: "alice.johnson@company.com",
    role: "Admin",
    status: "Active",
    lastActive: "2 hours ago",
  },
  {
    id: 2,
    name: "Bob Smith",
    email: "bob.smith@company.com",
    role: "HR Manager",
    status: "Active",
    lastActive: "1 day ago",
  },
  {
    id: 3,
    name: "Carol Lee",
    email: "carol.lee@company.com",
    role: "Recruiter",
    status: "Suspended",
    lastActive: "3 days ago",
  },
  {
    id: 4,
    name: "David Kim",
    email: "david.kim@company.com",
    role: "Recruiter",
    status: "Active",
    lastActive: "5 hours ago",
  },
  {
    id: 5,
    name: "Eva Green",
    email: "eva.green@company.com",
    role: "HR Manager",
    status: "Suspended",
    lastActive: "2 weeks ago",
  },
];

import { create } from "zustand";
import { toast } from "sonner";
import axios from "axios";

export type UserStatus = "Active" | "Suspended";
export type UserRole = "Admin" | "HR Manager" | "Recruiter";

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  status: UserStatus;
  lastActive: string;
}

interface NewUser {
  name: string;
  email: string;
  role: UserRole;
  password: string;
}


interface AdminStore {
    newUsers: NewUser[];
    users: User[];
    addUser: (user: NewUser) => void;
    fetchUsers: () => void;
    editUser: (updatedUser: User) => void;
    deleteUser: (userId: number) => void;
    resetPassword: (userId: number, newPassword: string) => void;
    searchUser: (query: string) => User[];
    loading: boolean;
    error: string | null;
}

// Move getUserStats outside of the zustand store definition
export function getUserStats(users: User[]) {
  const total = users.length;
  const active = users.filter(u => u.status === "Active").length;
  const suspended = users.filter(u => u.status === "Suspended").length;
  return {
    total,
    active,
    suspended,
  };
}

export const useAdminStore = create<AdminStore>((set, get) => ({
  users: [],
  newUsers: [],
  loading: false,
  error: null,
  addUser: async (user) => {
    set({ loading: true, error: null });
    try {
      // Replace with your actual API endpoint
      const res = await fetch("/api/admin/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.message || "Failed to add user");
      }

      set((state) => ({
        newUsers: [...state.newUsers, user],
        loading: false,
        error: null,
      }));
      toast.success("User added!");
    } catch (err: any) {
        const newDummyUser = {
          id: Date.now(),
          name: user.name,
          email: user.email,
          role: user.role,
          status: "Active" as UserStatus, // <-- fix here
          lastActive: "Just now",
        };
        dummyUsers.push(newDummyUser); // <-- append to dummyUsers array

        set(() => ({
          users: [...dummyUsers], // always use dummyUsers as source
          loading: false,
          error: "API failed, user added to dummy data.",
        }));
        toast.error("API failed, user added to dummy data.");
  }
  },
  fetchUsers: async () => {
    set({ loading: true, error: null });
    try {
      const res = await axios.get<User[]>("/api/admin/users");
      if (Array.isArray(res.data)) {
      set({ users: res.data, loading: false, error: null });
    } else {
      throw new Error("Unexpected response format");
    }
    } catch (err: any) {
      set({ users: dummyUsers, loading: false, error: "Failed to fetch users, showing dummy data." });
      toast.error("Failed to fetch users, showing dummy data.");
    }
  },
  editUser: async (updatedUser) => {
    try {
      const res = await axios.put(`/api/admin/users/${updatedUser.id}`, updatedUser);
      if (!res.data || res.status !== 200) throw new Error("Failed to update user");

      set((state) => ({
        users: state.users.map((user) =>
          user.id === updatedUser.id ? { ...user, ...updatedUser } : user
        ),
      }));

      toast.success("User updated!");
    } catch (err) {
      // Fallback to dummy update
      set((state) => ({
        users: state.users.map((user) =>
          user.id === updatedUser.id ? { ...user, ...updatedUser } : user
        ),
        error: "Failed to update user on server. Dummy data updated.",
      }));
      toast.error("Failed to update user on server. Dummy data updated.");
    }
  },

  deleteUser: async (userId) => {
    try {
      const res = await axios.delete(`/api/admin/users/${userId}`);
      if (res.status !== 200) throw new Error("Failed to delete user");

      set((state) => ({
        users: state.users.filter((user) => user.id !== userId),
      }));

      toast.success("User deleted!");
    } catch (err) {
      // Fallback to dummy delete
      set((state) => ({
        users: state.users.filter((user) => user.id !== userId),
        error: "Failed to delete user on server. Dummy data updated.",
      }));
      toast.error("Failed to delete user on server. Dummy data updated.");
    }
  },
  resetPassword: async (userId: number, newPassword: string) => {
  set({ loading: true, error: null });
  try {
    const res = await axios.post(`/api/admin/users/${userId}/reset-password`, {
      password: newPassword,
    });
    if (res.status !== 200) throw new Error("Failed to reset password");

    toast.success("Password reset successfully!");
    set({ loading: false, error: null });
  } catch (err: any) {
    set({ loading: false, error: "Failed to reset password" });
    toast.error("Failed to reset password");
  }
},
searchUser: (query: string) => {
    const users = get().users; // <-- FIXED: get is available
    const lowerQuery = query.toLowerCase();
    return users.filter(
      user =>
        user.name.toLowerCase().includes(lowerQuery) ||
        user.email.toLowerCase().includes(lowerQuery) ||
        user.role.toLowerCase().includes(lowerQuery) ||
        user.status.toLowerCase().includes(lowerQuery)
    );
  },

}));

