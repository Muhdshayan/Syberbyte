import { create } from "zustand";
import axios from "axios";
import { toast } from "sonner";

const dummyJobs: Job[] = [
  {
    job_id: 1,
    posted_by: 4,
    assigned_to: 5,
    date_posted: "2025-07-15T10:00:00Z",
    description: "Build and maintain REST APIs using Django.",
    education_level: "Bachelor's in Computer Science",
    experience_level: "2+ years",
    industry: "Information Technology",
    is_active: true,
    job_type: "Full-time",
    location: "Remote",
    role: "Backend Developer",
    salary: "70000.00",
    salary_currency: "USD",
    salary_period: "year",
    skills: "Python, Django, REST, PostgreSQL",
  },
];

export interface Job {
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

interface hrStore {
    jobs: Job[];
    loading: boolean;
    error: string | null;
    fetchJobs: () => Promise<void>;
    addJob: (job: Job) => void;
    updateJob: (id: number, updatedJob: Partial<Job>) => void;
    deleteJob: (id: number) => void;
}

export const useHrStore = create<hrStore>((set) => ({
  jobs: [],
  loading: false,
  error: null,

  fetchJobs: async () => {
    set({ loading: true, error: null });
    try {
      const res = await axios.get<Job[]>("http://localhost:8000/api/jobdetails/");
      if (!res.data || !Array.isArray(res.data)) {
        throw new Error("Invalid data format");
      }
      // Map API data to Job interface
      const mappedJobs = res.data.map(job => ({
        job_id: job.job_id,
        posted_by: job.posted_by,
        assigned_to: job.assigned_to,
        date_posted: new Date(job.date_posted).toLocaleString("en-GB", {
                      year: "numeric",
                      month: "2-digit",
                      day: "2-digit",
                      hour: "2-digit",
                      minute: "2-digit",
                      hour12: false,
                      timeZone: "UTC",
                    }).replace(",", ""), // "14/07/2025 08:00"
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
      set({ jobs: mappedJobs, loading: false, error: null });
    } catch (err) {
      toast.error("Failed to fetch jobs");
      set({ jobs: dummyJobs, loading: false, error: "Failed to fetch from API. Showing dummy data." });
    }
  },

  addJob: (job) => {
    set((state) => ({ jobs: [...state.jobs, job] }));
    toast.success("Job added successfully");
  },

  updateJob: (id, updatedJob) => {
    set((state) => ({
      jobs: state.jobs.map((job) =>
        job.job_id === id ? { ...job, ...updatedJob } : job
      ),
    }));
    toast.success("Job updated successfully");
  },

  deleteJob: (id) => {
    set((state) => ({
      jobs: state.jobs.filter((job) => job.job_id !== id),
    }));
    toast.success("Job deleted successfully");
  },
}));