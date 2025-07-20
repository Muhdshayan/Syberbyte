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

const dummyCandidates: Candidate[] = [
  {
    id: "1",
    jobId: 1,
    name: "1",
    score: 92,
    recommendation: "Strong hire - Excellent technical skills and cultural fit",
    role: "Frontend Developer",
    experience: "Mid-Level (2-4 years)",
    breakdown: { technical: 98, experience: 95, cultural: 85 },
    summary:
      "Experienced Full Stack Developer with 4.5+ years of hands-on experience in designing, developing, and deploying scalable web applications. Proficient in both frontend and backend technologies with a strong focus on React.js, Node.js, and cloud-native solutions. Passionate about building user-centric products, improving performance, and collaborating in agile teams.",
    skills: "Javascript, MongoDB, AWS, Reactjs, Nodejs",
    experienceList: [
      {
        title: "Software Engineer",
        company: "VibeTech Solutions",
        duration: "June 2021 – Present",
        location: "Karachi (Remote)",
        description:
          "Full Stack Developer with 4.5+ years of experience building scalable web applications using React.js, Node.js, and cloud technologies",
      },
    ],
  },
  {
    id: "2",
    jobId: 2,
    name: "2",
    score: 85,
    recommendation: "Hire - Good technical background, needs minor upskilling.",
    role: "Backend Developer",
    experience: "Mid-Level (2-4 years)",
    breakdown: { technical: 90, experience: 88, cultural: 80 },
    summary:
      "Backend developer with strong Node.js and SQL skills. Good at building APIs and optimizing performance.",
    skills: "Node.js, SQL, Express, Docker",
    experienceList: [
      {
        title: "Backend Developer",
        company: "DataSoft",
        duration: "Jan 2022 – Present",
        location: "Remote",
        description:
          "Developed RESTful APIs and managed database integrations for multiple SaaS products.",
      },
    ],
  },
  {
    id: "3",
    jobId: 3,
    name: "3",
    score: 78,
    recommendation: "Consider - Average skills, but shows potential for growth.",
    role: "UI/UX Designer",
    experience: "Junior (1-2 years)",
    breakdown: { technical: 75, experience: 70, cultural: 80 },
    summary:
      "Creative UI/UX designer with a passion for user-centered design and improving digital experiences.",
    skills: "Figma, Sketch, Adobe XD",
    experienceList: [
      {
        title: "UI/UX Designer",
        company: "Designify",
        duration: "Mar 2023 – Present",
        location: "Remote",
        description:
          "Worked on mobile and web UI projects for various clients, focusing on usability and accessibility.",
      },
    ],
  },
  {
    id: "4",
    jobId: 4,
    name: "4",
    score: 65,
    recommendation: "Weak fit - Lacks some required skills, but good attitude.",
    role: "QA Engineer",
    experience: "Junior (1-2 years)",
    breakdown: { technical: 60, experience: 65, cultural: 70 },
    summary:
      "QA Engineer with experience in manual and automated testing. Good attitude and eager to learn.",
    skills: "Selenium, Jest, Cypress",
    experienceList: [
      {
        title: "QA Engineer",
        company: "Testify",
        duration: "Feb 2023 – Present",
        location: "Remote",
        description:
          "Performed manual and automated testing for web applications, ensuring quality releases.",
      },
    ],
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

export interface Candidate {
  id: any;
  jobId: any;
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

  // Existing methods
  fetchJobs: () => Promise<void>;
  fetchCandidates: (jobId?: number) => Promise<void>;
  RejectCandidate: (candidateId: string, jobId: number) => Promise<void>;
  ReferToHr: (candidateId: string, jobId: number) => Promise<void>;

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
      set({ jobs: mappedJobs, loading: false, error: null });
    } catch (err) {
      toast.error("Failed to fetch jobs");
      set({ jobs: dummyJobs, loading: false, error: "Failed to fetch from API. Showing dummy data." });
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
        jobId: item.job.job_id,
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
    } catch (err) {
      set({ candidates: dummyCandidates, loading: false, error: "Failed to fetch candidates. Showing dummy data." });
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


  RejectCandidate: async (candidateId: any, jobId: any) => {
    try {
      await axios.post(`/api/recruiter/${jobId}/candidates/${candidateId}/reject`);
      toast.success("Candidate rejected successfully");
      await get().fetchCandidates(jobId);
    } catch (error) {
      toast.error("Failed to reject candidate");
      console.error(error);
    }
  },
  ReferToHr: async (candidateId: any, jobId: any) => {
    try {
      await axios.post(`/api/recruiter/${jobId}/candidates/${candidateId}/refer-to-hr`);
      toast.success("Candidate referred to HR successfully");
      await get().fetchCandidates(jobId);
    } catch (error) {
      toast.error("Failed to refer candidate to HR");
      console.error(error);
    }
  },
}));