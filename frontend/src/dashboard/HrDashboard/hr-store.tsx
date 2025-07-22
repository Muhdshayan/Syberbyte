import { create } from "zustand";
import axios from "axios";
import { toast } from "sonner";


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
export interface Candidate {
  id: any;
  jobId: any;
  name: string;
  score: number;
  status: string;
  recommendation: string;
  role: string;
  experience: string;
  breakdown: {
    technical: number;
    experience: number;
    cultural: number;
  };
  summary: string;
  skills: string;
  experienceList: {
    title: string;
    company: string;
    duration: string;
    location: string;
    description: string;
  }[];
}

interface hrStore {
    jobs: Job[];
    candidates: Candidate[];
    loading: boolean;
    error: string | null;
    fetchJobs: () => Promise<void>;
    addJob: (job: Job) => void;
    updateJob: (id: number, updatedJob: Partial<Job>) => void;
    deleteJob: (id: number) => void;
    fetchCandidates: () => Promise<void>;
}

export const useHrStore = create<hrStore>((set) => ({
  jobs: [],
  loading: false,
  error: null,
  candidates: [],
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
                    }).replace(",", ""),
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
      console.log("hr store jobs:", res)
      set({ jobs: mappedJobs, loading: false, error: null });
    } catch (err) {
      toast.error("Failed to fetch jobs");
      set({ loading: false, error: "Failed to fetch from API. Showing dummy data." });
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
   fetchCandidates: async () => {
    set({ loading: true, error: null });
    try {
      const res = await axios.get<Candidate[]>("http://localhost:8000/api/jobapplication/");
      if (!res.data || !Array.isArray(res.data)) {
        throw new Error("Invalid data format");
      }
      // Map API data to candidate interface
      const mappedCandidates = res.data.map((item: any) => ({
        id: item.candidate.candidate_id,
        jobId: item.job.job_id,
        status:item.status,
        name: item.candidate.name,
        score: item.score ?? 0,
        recommendation: item.ai_recommendation ?? "",
        role: item.job.role,
        experience: "",
        breakdown: {
          technical: item.technical_score,
          experience: item.experience_score,
          cultural: item.cultural_score,
        },
        summary: item.candidate.summary,
        skills: item.candidate.technical_skills + item.candidate.soft_skills,
        experienceList: (item.candidate.work_experiences || []).map((exp: any) => ({
          title: exp.role,
          company: exp.company_name,
          duration: `${exp.start_year} - ${exp.end_year ?? "Present"}`,
          location: "",
          description: exp.summary,
        })),
      }));
      console.log("candidates:", res)
      set({ candidates: mappedCandidates, loading: false, error: null });
    } catch (err) {
      set({loading: false, error: "Failed to fetch candidates. Showing dummy data." });
    }
  },
}));