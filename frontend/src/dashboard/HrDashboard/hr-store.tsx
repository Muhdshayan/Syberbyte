import { create } from "zustand";
import axios from "axios";
import { toast } from "sonner";

const dummyJobs: Job[] = [
  {
    id: 1,
    title: "Software Engineer",
    description:
      "We're looking for a passionate Frontend Developer to join our product team and bring designs to life using React.js. You'll work closely with designers and backend engineers to build fast, intuitive, and responsive web apps.",
    location: "Remote",
    type: "Full-time",
    salary: "$60,000/year",
    postedOn: "07/01/25",
  },
  {
    id: 2,
    title: "Backend Developer",
    description:
      "Join our backend team to help build scalable APIs using Node.js and PostgreSQL. You'll design robust systems and optimize performance.",
    location: "Lahore, PK",
    type: "Contract",
    salary: "$45/hour",
    postedOn: "06/29/25",
  },
  {
    id: 3,
    title: "UI/UX Designer",
    description:
      "We're seeking a creative UI/UX designer to craft intuitive interfaces and deliver amazing user experiences across all devices.",
    location: "Remote",
    type: "Internship",
    salary: "$1,000/month",
    postedOn: "07/03/25",
  },
  {
    id: 4,
    title: "DevOps Engineer",
    description:
      "You will manage CI/CD pipelines, monitor system performance, and ensure high availability of services using AWS and Docker.",
    location: "Karachi, PK",
    type: "Full-time",
    salary: "$75,000/year",
    postedOn: "06/28/25",
  },
  {
    id: 5,
    title: "AI/ML Engineer",
    description:
      "Work on cutting‑edge AI projects including NLP, recommendation systems, and predictive analytics. Experience with Python and TensorFlow required.",
    location: "Hybrid (Islamabad)",
    type: "Full-time",
    salary: "$90,000/year",
    postedOn: "06/27/25",
  },
];

export interface Job {
  id: number;
  title: string;
  description: string;
  location: string;
  type: string;
  salary: string;
  postedOn: string;
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
      const res = await axios.get<[]>("/api/hr/jobs");
      if (!res.data || !Array.isArray(res.data)) {
        throw new Error("Invalid data format");
      }
      set({ jobs: res.data, loading: false });
    } catch (error: any) {
      set({ jobs:dummyJobs, loading: false, error: error.message });
      toast.error("Failed to fetch jobs");
    }
  },

  addJob: (job) => {
    set((state) => ({ jobs: [...state.jobs, job] }));
    toast.success("Job added successfully");
  },

  updateJob: (id, updatedJob) => {
    set((state) => ({
      jobs: state.jobs.map((job) =>
        job.id === id ? { ...job, ...updatedJob } : job
      ),
    }));
    toast.success("Job updated successfully");
  },

  deleteJob: (id) => {
    set((state) => ({
      jobs: state.jobs.filter((job) => job.id !== id),
    }));
    toast.success("Job deleted successfully");
  },
}));