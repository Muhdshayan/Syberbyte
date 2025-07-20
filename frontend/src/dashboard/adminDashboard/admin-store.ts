
import { create } from "zustand";
import { toast } from "sonner";
import axios from "axios";
//import type { ReactNode } from "react";

export type UserStatus = "Active" | "Suspended";

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  status: UserStatus;
  lastActive: string;
}

interface NewUser {
  name: string;
  email: string;
  role: String;
  password: string;
}

export interface JobCategory {
  job_id: number;
  posted_by: number,
  assigned_to: number;
  date_posted: string;
  description: string;
  education_level: string;
  experience_level: string;
  industry: string;
  is_active: boolean;
  job_type: string;
  location: string;
  role: string;
  salary: string;
  salary_currency: string;
  salary_period: string;
  skills: string;
}


interface AdminStore {
    newUsers: NewUser[];
    users: User[];
    searchCategory: (query: string) => JobCategory[]
    addUser: (user: NewUser) => void;
    fetchUsers: () => Promise<void>;
    editUser: (updatedUser: User) => void;
    deleteUser: (userId: number) => void;
    resetPassword: (userId: number, newPassword: string) => void;
    searchUser: (query: string) => User[];
    jobCategories: JobCategory[];
    fetchJobCategories: () => Promise<void>;
    editCategory: (category: JobCategory) => Promise<void>;
    deleteCategory: (job_id: number) => Promise<void>;
    addCategory: (category: JobCategory) => Promise<void>;
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

export function getCategoryStats(categories: JobCategory[]) {
  const total = categories.length;
  const roles = categories.map(c => c.role);
  const uniqueRoles = Array.from(new Set(roles));
  return {
    total,
    uniqueRoles,
  };
}

// Add this utility function at the top or in a utils file
function formatRole(role: string) {
  return role
    .replace(/_/g, " ") // replace underscores with spaces
    .replace(/\b\w/g, (char) => char.toUpperCase()); // capitalize first letter of each word
}

export const useAdminStore = create<AdminStore>((set, get) => ({
  users: [],
  newUsers: [],
  jobCategories: [],
  loading: false,
  error: null,
  addUser: async (user) => {
    set({ loading: true, error: null });
    try {
      // Replace with your actual API endpoint
      console.log(user)
      const res = await fetch("http://localhost:8000/api/useraccounts/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.message || "Failed to add user");
      }

      await get().fetchUsers();

      set({ loading: false, error: null });
      toast.success("User added!");
    } catch (err: any) {
        set(() => ({ 
          loading: false,
          error: "API failed, user added to dummy data.",
        }));
        toast.error("API failed, user added to dummy data.");
  }
  },
  fetchUsers: async () => {
    set({ loading: true, error: null });
    try {
      const res = await axios.get<User[]>("http://localhost:8000/api/useraccounts/");
      console.log(res)
      // Map API data to candidate interface
      
      
      const mappedUser = res.data.map((item: any) => ({
        id: item.user_id,
        name: item.name,
        email: item.email,
        role: formatRole(item.role),
        status: "Active" as UserStatus,
        lastActive: new Date(item.time).toLocaleString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            hour12: true,
          }),   
      }));

      set({ users: mappedUser, loading: false, error: null });
    } catch (err: any) {
      set({ loading: false, error: "Failed to fetch users, showing dummy data." });
      toast.error("Failed to fetch users, showing dummy data.");
    }
  },
  editUser: async (updatedUser) => {
    try {
      const res = await axios.put(`/api/admin/users/${updatedUser.id}`, updatedUser);
      if (!res.data || res.status !== 200) throw new Error("Failed to update user");

      await get().fetchUsers();

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
      console.log(userId)
      const res = await axios.delete(`http://localhost:8000/api/useraccounts/${userId}/`);
      if (res.status !== 200) throw new Error("Failed to delete user");

      await get().fetchUsers();

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
  fetchJobCategories: async () => {
  set({ loading: true, error: null });
    try {
      const res = await axios.get<JobCategory[]>("http://localhost:8000/api/jobdetails/");
      if (!res.data || !Array.isArray(res.data)) {
        throw new Error("Invalid data format");
      }
      // Map API data to Job interface
      const mappedJobs = res.data.map(job => ({
        job_id: job.job_id,
        posted_by: job.posted_by,
        assigned_to: job.assigned_to,
        date_posted: job.date_posted,
        description: job.description,
        education_level: job.education_level,
        experience_level: job.experience_level,
        industry: job.industry,
        is_active: job.is_active,
        job_type: job.job_type,
        location: job.location,
        role: job.role,
        salary: job.salary,
        salary_currency: job.salary_currency,
        salary_period: job.salary_period,
        skills: job.skills,
      }));
      set({ jobCategories: mappedJobs, loading: false, error: null });
    } catch (err) {
      toast.error("Failed to fetch jobs");
      set({loading: false, error: "Failed to fetch from API. Showing dummy data." });
    }
  },
  editCategory: async (updatedCategory: JobCategory) => {
    set({ loading: true, error: null });
    try {
      const res = await axios.put(`/api/admin/job-categories/${updatedCategory.role}`, updatedCategory);
      if (!res.data || res.status !== 200) throw new Error("Failed to update category");

      await get().fetchJobCategories();
      toast.success("Category updated!");
    } catch (err) {
      // Fallback to dummy update
      set((state) => ({
        jobCategories: state.jobCategories.map((cat) =>
          cat.role === updatedCategory.role ? { ...cat, ...updatedCategory } : cat
        ),
        loading: false,
        error: "Failed to update category on server. Dummy data updated.",
      }));
      toast.error("Failed to update category on server. Dummy data updated.");
    }
  },
  deleteCategory: async (job_id: number) => {
  set({ loading: true, error: null });
  try {
    const res = await axios.delete(`http://localhost:8000/api/jobdetails/${job_id}/`); // Ensure the endpoint uses job_id
    if (res.status !== 200) throw new Error("Failed to delete category");

    await get().fetchJobCategories();
    toast.success("Category deleted!");
  } catch (err) {
    // Fallback to dummy delete
    set((state) => ({
      jobCategories: state.jobCategories.filter((cat) => cat.job_id !== job_id),
      loading: false,
      error: "Failed to delete category on server. Dummy data updated.",
    }));
    toast.error("Failed to delete category on server. Dummy data updated.");
  }
},
  addCategory: async (category: JobCategory) => {
    set({ loading: true, error: null });
    try {
      const { job_id, ...categoryWithoutJobId } = category;
      console.log(categoryWithoutJobId); // Log the payload without job_id
      const res = await axios.post("http://localhost:8000/api/jobdetails/", categoryWithoutJobId);
      if (!res.data || res.status !== 201) throw new Error("Failed to add category");

      await get().fetchJobCategories();
      toast.success("Category added!");
    } catch (err) {
      set((state) => ({
        jobCategories: [...state.jobCategories, category],
        loading: false,
        error: "Failed to add category on server. Dummy data updated.",
      }));
      toast.error("Failed to add category on server. Dummy data updated.");
    }
  },
  searchCategory: (query: string) => {
  const categories = get().jobCategories;
  const lowerQuery = query.toLowerCase();
  console.log("Searching categories with query:", lowerQuery);
  return categories.filter(cat =>
    cat.industry.toLowerCase().includes(lowerQuery) ||
    cat.role.toLowerCase().includes(lowerQuery) ||
    `${cat.industry} ${cat.role}`.toLowerCase().includes(lowerQuery) || // <-- add this line
    cat.experience_level.toLowerCase().includes(lowerQuery) ||
    cat.salary.toLowerCase().includes(lowerQuery) ||
    cat.skills
      .split(',')
      .map(skill => skill.trim().toLowerCase())
      .some(skill => skill.includes(lowerQuery))
  );
},
}));

