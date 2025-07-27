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
  application_id: any;
  candidate_id: any;
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
  hasUnsavedChanges: boolean;
  changedCandidates: Set<string>;
  fetchJobs: () => Promise<void>;
  addJob: (job: Job) => void;
  updateJob: (id: number, updatedJob: Partial<Job>) => void;
  deleteJob: (job_id: number) => Promise<void>;
  fetchCandidates: () => Promise<void>;
  updateCandidateStatusLocally: (candidateId: number, jobId: number, newStatus: string) => void;
  resetUnsavedChanges: () => void;
  editCandidates: (updatedCandidates: Candidate[]) => Promise<void>;
  submitFeedback: (feedbackData: {
    candidateId: number;
    jobId: number;
    feedback: string;
    correctScore: number;
    timestamp: string;
  }) => Promise<void>;
  generateExcelReport: (jobId?: number, reportType?: string) => Promise<void>
}

export const useHrStore = create<hrStore>((set, get) => ({
  jobs: [],
  loading: false,
  error: null,
  candidates: [],
  hasUnsavedChanges: false,
  changedCandidates: new Set(),
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

  addJob: async (jobData) => {
    set({ loading: true, error: null });
    try {
      console.log("Adding job with data:", jobData);

      const res = await axios.post("http://localhost:8000/api/jobdetails/", jobData);

      if (res.status === 201 || res.status === 200) {
        // Add the new job to the state with the returned ID
        const newJob = {
          ...jobData,
          job_id: res.data.job_id || res.data.id, // Use the ID returned from server
          date_posted: new Date().toLocaleString("en-GB", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            hour12: false,
            timeZone: "UTC",
          }).replace(",", ""),
        };

        set((state) => ({
          jobs: [...state.jobs, newJob],
          loading: false,
          error: null
        }));

        toast.success("Job added successfully!");
        console.log("Job added successfully:", res.data);
      } else {
        throw new Error(`Server responded with status: ${res.status}`);
      }
    } catch (err: any) {
      console.error("Error adding job:", err);

      const errorMessage = err.response?.data?.message ||
        err.response?.data?.error ||
        err.message ||
        "Failed to add job";

      set({ loading: false, error: errorMessage });
      toast.error(`Failed to add job: ${errorMessage}`);

      // Re-throw the error so the calling component can handle it
      throw err;
    }
  },

  updateJob: (id, updatedJob) => {
    set((state) => ({
      jobs: state.jobs.map((job) =>
        job.job_id === id ? { ...job, ...updatedJob } : job
      ),
    }));
    toast.success("Job updated successfully");
  },

  deleteJob: async (job_id: number) => {
    set({ loading: true, error: null });
    try {
      const res = await axios.delete(`http://localhost:8000/api/jobdetails/${job_id}/`); // Ensure the endpoint uses job_id
      if (res.status !== 200) throw new Error("Failed to delete category");

      await get().fetchJobs();
      toast.success("Category deleted!");
    } catch (err) {
      // Fallback to dummy delete
      set((state) => ({
        job: state.jobs.filter((cat) => cat.job_id !== job_id),
        loading: false,
        error: "Failed to delete category on server. Dummy data updated.",
      }));
      toast.error("Failed to delete category on server. Dummy data updated.");
    }
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
        candidate_id: item.candidate.candidate_id,
        application_id: item.application_id,
        jobId: item.job.job_id,
        status: item.status,
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
      console.log("candidates:", mappedCandidates)
      set({ candidates: mappedCandidates, loading: false, error: null });
    } catch (err) {
      set({ loading: false, error: "Failed to fetch candidates. Showing dummy data." });
    }
  },
  updateCandidateStatusLocally: (candidateId: number, jobId: number, newStatus: string) => {
    const state = get();

    console.log("Updating candidate locally:", { candidateId, jobId, newStatus }); // Debug log

    const updatedCandidates = state.candidates.map(candidate => {
      // Convert candidateId to number if it's a string, or use === for exact match
      const numericCandidateId = typeof candidateId === 'string' ? parseInt(candidateId) : candidateId;

      if (candidate.candidate_id === numericCandidateId && candidate.jobId === jobId) {
        console.log("Found candidate to update:", candidate.name, "from", candidate.status, "to", newStatus); // Debug log
        return { ...candidate, status: newStatus };
      }
      return candidate;
    });

    const newChangedCandidates = new Set(state.changedCandidates);
    newChangedCandidates.add(`${candidateId}-${jobId}`);

    console.log("Updated candidates:", updatedCandidates); // Debug log
    console.log("Changed candidates:", newChangedCandidates); // Debug log

    set({
      candidates: updatedCandidates,
      hasUnsavedChanges: true,
      changedCandidates: newChangedCandidates
    });

    // Add toast to confirm the change
    toast.success(`Candidate status updated to ${newStatus}`);
  },

  resetUnsavedChanges: () => {
    set({
      hasUnsavedChanges: false,
      changedCandidates: new Set()
    });
  },
  editCandidates: async (updatedCandidates: Candidate[]) => {
    set({ loading: true, error: null });
    try {
      const res = await axios.put("http://localhost:8000/api/jobapplication/update/", updatedCandidates);
      if (res.status === 200) {

        set({ loading: false, error: null });
        const results = res.data.results;

        toast.success("Candidates updated successfully");
        console.log("Candidates updated successfully:", results);
      }
    } catch (err) {
      console.error(err);
      set({ loading: false, error: "Failed to update candidates." });
      console.error("Error updating candidates:", err);
      toast.error("Failed to update candidates");
    }
  },
  submitFeedback: async (feedbackData) => {
    set({ loading: true, error: null });
    try {
      console.log("Submitting feedback with data:", feedbackData);

      const res = await axios.post("http://localhost:8000/api/feedback/", {
        candidate_id: feedbackData.candidateId,
        job_id: feedbackData.jobId,
        feedback_text: feedbackData.feedback,
        suggested_score: feedbackData.correctScore,
      });

      if (res.status === 200 || res.status === 201) {
        set({ loading: false, error: null });
        toast.success("Feedback submitted successfully!");
        console.log("Feedback submitted successfully:", res.data);
      } else {
        throw new Error(`Server responded with status: ${res.status}`);
      }
    } catch (err: any) {
      console.error("Error submitting feedback:", err);
      set({ loading: false, error: err });
      toast.error(`Failed to submit feedback: ${err.message || "Unknown error"}`);
    }
  },
  generateExcelReport: async (jobId?: number) => {
    console.log(jobId)
    set({ loading: true, error: null });
    try {
      console.log("Generating Excel report...");

      const response = await axios.get("http://localhost:8000/api/jobapplication/export/", {
        params: jobId ? { job_id: jobId } : {},
        responseType: 'blob',
      });


      // Create blob from response data
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });

      // Create download link and trigger download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `HR_Report_${jobId ? `Job${jobId}_` : ''}${Date.now()}.xlsx`;

      // Add to DOM, click, and remove
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Cleanup blob URL
      window.URL.revokeObjectURL(url);

      set({ loading: false });
      toast.success("Excel report downloaded successfully!");

    } catch (err: any) {
      console.error("Error generating Excel report:", err);
      set({ loading: false, error: "Failed to generate report" });
      toast.error("Failed to generate Excel report");
    }
  },
}));