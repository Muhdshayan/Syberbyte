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
  id: number;
  title: string;
  description: string;
  location: string;
  type: string;
  salary: string;
  postedOn: string;
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
  type: "resume" | "excel";
  file?: File; // Store actual file for upload
}

export interface BulkUploadResult {
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
      const res = await axios.get<Job[]>("/api/recruiter/jobs");
      if (!res.data || !Array.isArray(res.data)) {
        throw new Error("Invalid data format");
      }
      set({ jobs: res.data, loading: false, error: null });
    } catch (err) {
      toast.error("Failed to fetch jobs");
      set({ jobs: dummyJobs, loading: false, error: "Failed to fetch from API. Showing dummy data." });
    }
  },
  
  fetchCandidates: async () => {
    set({ loading: true, error: null });
    try {
      const res = await axios.get<Candidate[]>(`/api/recruiter//candidates`);
      if (!res.data || !Array.isArray(res.data)) {
        throw new Error("Invalid data format");
      }
      set({ candidates: res.data, loading: false, error: null });
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
      
      // Add all files
      uploadFiles.forEach((uploadFile, index) => {
        if (uploadFile.file) {
          formData.append(`files`, uploadFile.file);
          formData.append(`fileTypes`, uploadFile.type);
        }
      });
      
      const result = await axios.post<BulkUploadResult>("/api/recruiter/bulk-upload", formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = progressEvent.total 
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0;
          set({ uploadProgress: progress });
        }
      });
      
      // Mark all files as completed
      set((state) => ({
        uploadFiles: state.uploadFiles.map(f => ({
          ...f,
          status: 'completed' as const,
          progress: 100
        }))
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
        )
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