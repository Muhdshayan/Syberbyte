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
  application_id: any;
  jobId: any;
  cv:string;
  status:string
  name: string;
  score: number;
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

// New interfaces for bulk upload
export interface UploadFile {
  id: string;
  name: string;
  size: number;
  status: "pending" | "processing" | "completed" | "error";
  progress: number;
  errorMessage?: string;
  type: "pdf" | "docx" | "doc";
  file?: File;
}


export interface BulkUploadResult {
  files: any;
  totalFiles: number;
  successCount: number;
  errorCount: number;
  errors: Array<{
    fileName: string;
    error: string;
  }>;
  newCandidates: Candidate[];
}

interface RecruiterStore {
  jobs: Job[];
  candidates: Candidate[];
  loading: boolean;
  error: string | null;

  // Bulk upload state
  uploadFiles: UploadFile[];
  uploadProgress: number;
  isUploading: boolean;
  uploadError: string | null;
  hasUnsavedChanges: boolean;
  changedCandidates: Set<string>;

  // Existing methods
  fetchJobs: () => Promise<void>;
  fetchCandidates: (jobId?: number) => Promise<void>;
  updateCandidateStatusLocally: (candidateId: number, jobId: number, newStatus: string) => void;
  resetUnsavedChanges: () => void;
  editCandidates: (updatedCandidates: Candidate[]) => Promise<void>;
  // New bulk upload methods
  addUploadFiles: (files: UploadFile[]) => void;
  removeUploadFile: (fileId: string) => void;
  clearUploadFiles: () => void;
  updateFileProgress: (fileId: string, progress: number) => void;
  updateFileStatus: (fileId: string, status: UploadFile['status'], errorMessage?: string) => void;
  processBulkUpload: (jobId: number) => Promise<BulkUploadResult>;
}


export const useRecruiterStore = create<RecruiterStore>((set, get) => ({
  jobs: [],
  candidates: [],
  loading: false,
  error: null,

  // Bulk upload initial state
  uploadFiles: [],
  uploadProgress: 0,
  isUploading: false,
  uploadError: null,
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
      set({ jobs: mappedJobs, loading: false, error: null });
    } catch (err) {
      toast.error("Failed to fetch jobs");
      set({ loading: false, error: "Failed to fetch from API. Showing dummy data." });
    }
  },

  fetchCandidates: async () => {
    set({ loading: true, error: null });
    try {
      const res = await axios.get<Candidate[]>("http://localhost:8000/api/jobapplication/");
      console.log(res)
      if (!res.data || !Array.isArray(res.data)) {
        throw new Error("Invalid data format");
      }
      // Map API data to candidate interface
      const mappedCandidates = res.data.map((item: any) => ({
        id: item.candidate.candidate_id,
        application_id: item.application_id,
        jobId: item.job.job_id,
        cv:item.cv,
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
      set({ candidates: mappedCandidates, loading: false, error: null });
      console.log("candidates:", res);
    } catch (err) {
      set({loading: false, error: "Failed to fetch candidates. Showing dummy data." });
    }
  },

    editCandidates: async (updatedCandidates: Candidate[]) => {
      set({ loading: true, error: null });
      try {
        const res = await axios.put("http://localhost:8000/api/jobapplication/update/", updatedCandidates);
        console.log(updatedCandidates);
        if (res.status === 200 || res.status === 207) {
  
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


  // Bulk upload methods
  addUploadFiles: (files: UploadFile[]) => {
    set((state) => ({
      uploadFiles: [...state.uploadFiles, ...files]
    }));
  },

  removeUploadFile: (fileId: string) => {
    set((state) => ({
      uploadFiles: state.uploadFiles.filter(f => f.id !== fileId)
    }));
  },

  clearUploadFiles: () => {
    set({
      uploadFiles: [],
      uploadProgress: 0,
      uploadError: null
    });
  },

  updateFileProgress: (fileId: string, progress: number) => {
    set((state) => ({
      uploadFiles: state.uploadFiles.map(f =>
        f.id === fileId ? { ...f, progress } : f
      )
    }));
  },

  updateFileStatus: (fileId: string, status: UploadFile['status'], errorMessage?: string) => {
    set((state) => ({
      uploadFiles: state.uploadFiles.map(f =>
        f.id === fileId ? { ...f, status, errorMessage } : f
      )
    }));
  },

  processBulkUpload: async (jobId: number) => {
    const { uploadFiles } = get();

    if (uploadFiles.length === 0) {
      throw new Error("No files to upload");
    }

    set({ isUploading: true, uploadError: null, uploadProgress: 0 });

    try {
      const formData = new FormData();

      // Add job ID
      formData.append('jobId', jobId.toString());

      // Add files with their types, using indexed keys for clarity
      uploadFiles.forEach((uploadFile) => {
        if (uploadFile.file) {
          formData.append('files', uploadFile.file);
          formData.append('fileTypes', uploadFile.type);
        }
      });

      const result = await axios.post<BulkUploadResult>("http://localhost:8000/api/upload-cv/", formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0;
          set({ uploadProgress: progress });
        },
      });

      // Mark all files as completed
      set((state) => ({
        uploadFiles: state.uploadFiles.map(f => ({
          ...f,
          status: 'completed' as const,
          progress: 100,
        })),
      }));

      await get().fetchCandidates();

      set({ isUploading: false });

      // Show success message
      if (result.data.successCount > 0) {
        toast.success(`Successfully processed ${result.data.successCount} files`);
      }

      // Show error summary if any
      if (result.data.errorCount > 0) {
        toast.error(`${result.data.errorCount} files failed to process`);
      }

      return result.data;

    } catch (error) {
      set({ isUploading: false, uploadError: "Upload failed" });

      // Mark all pending/processing files as error
      set((state) => ({
        uploadFiles: state.uploadFiles.map(f =>
          f.status === 'pending' || f.status === 'processing'
            ? { ...f, status: 'error' as const, errorMessage: 'Upload failed' }
            : f
        ),
      }));

      if (axios.isAxiosError(error)) {
        const errorMsg = error.response?.data?.message || "Upload failed";
        toast.error(errorMsg);
        throw new Error(errorMsg);
      }

      toast.error("Upload failed");
      throw error;
    }
  },
updateCandidateStatusLocally: (candidateId: number, jobId: number, newStatus: string) => {
  const state = get();
  
  console.log("Updating candidate locally:", { candidateId, jobId, newStatus }); // Debug log
  
  const updatedCandidates = state.candidates.map(candidate => {
    // Convert candidateId to number if it's a string, or use === for exact match
    const numericCandidateId = typeof candidateId === 'string' ? parseInt(candidateId) : candidateId;
    
    if (candidate.id === numericCandidateId && candidate.jobId === jobId) {
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
}));