import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { z } from "zod";
import { toast } from "sonner";
import { useHrStore } from "./hr-store";
import { useAuthStore } from "../../Login/useAuthStore";

// Zod schema for validation
const jobSchema = z.object({
  industry: z.string().min(1, "Industry is required"),
  role: z.string().min(1, "Role is required"),
  description: z.string().min(1, "Description is required"),
  location: z.string().min(1, "Location is required"),
  salary: z.string().min(1, "Salary is required"),
  salaryCurrency: z.string().min(1, "Currency is required"),
  salaryPeriod: z.string().min(1, "Salary period is required"),
  education: z.string().min(1, "Education is required"),
  skills: z.string().min(1, "Skills are required"),
  experience: z.string().min(1, "Experience is required"),
});

type JobForm = z.infer<typeof jobSchema>;

export default function AddJob() {
  const [form, setForm] = useState<JobForm>({
    industry: "",
    role: "",
    description: "",
    location: "",
    salary: "",
    salaryCurrency: "",
    salaryPeriod: "",
    education: "",
    skills: "",
    experience: "",
  });

  const [errors, setErrors] = useState<Partial<Record<keyof JobForm, string>>>({});
  
  // Get addJob function and loading state from HR store
  const addJob = useHrStore((state) => state.addJob);
  const loading = useHrStore((state) => state.loading);
  
  // Get auth user for posted_by field
  const authUser = useAuthStore((state) => state.authUser);

  const handleChange = (field: keyof JobForm, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    const result = jobSchema.safeParse(form);
    if (!result.success) {
      const fieldErrors: Partial<Record<keyof JobForm, string>> = {};
      for (const err of result.error.errors) {
        fieldErrors[err.path[0] as keyof JobForm] = err.message;
      }
      setErrors(fieldErrors);
      toast.error(result.error.errors[0].message);
      return;
    }

    // Check if user is authenticated - FIXED
    if (!authUser?.user_id) {
      toast.error("You must be logged in to create a job");
      return;
    }

    const currentDate = new Date().toISOString().split("T")[0];
    
    try {
      const jobData = {
        job_id: 1, // Will be set by backend
        industry: form.industry,
        role: form.role,
        description: form.description,
        location: form.location,
        salary: form.salary, // Convert to number
        salary_currency: form.salaryCurrency,
        salary_period: form.salaryPeriod, // Now uses form value
        education_level: form.education,
        skills: form.skills,
        experience_level: form.experience,
        posted_by: authUser.user_id, // Safe to use after null check
        assigned_to: 5, // Will be assigned later
        is_active: true,
        job_type: "Full-time", // Default or add to form
        date_posted: currentDate, // Format as YYYY-MM-DD
      };

      console.log("Submitting job data:", jobData);

      await addJob(jobData);
      
      // Reset form on success
      setForm({
        industry: "",
        role: "",
        description: "",
        location: "",
        salary: "",
        salaryCurrency: "",
        salaryPeriod: "",
        education: "",
        skills: "",
        experience: "",
      });
      setErrors({});
      
    } catch (error) {
      console.error("Error adding job:", error);
    }
  };

  return (
    <div className="flex items-center justify-center w-full">
      <form className="flex flex-col gap-5 md:w-[95%] w-[90%] font-inter-regular mt-8" onSubmit={handleSubmit}>
        <h2 className="text-3xl text-left font-poppins-semibold mb-2">Add New Job</h2>

        {/* Industry */}
        <div className="flex flex-col font-inter-regular gap-1">
          <Label>Industry</Label>
          <Input
            placeholder="e.g. IT, Finance"
            className="bg-white"
            value={form.industry}
            onChange={e => handleChange("industry", e.target.value)}
            disabled={loading}
          />
          {errors.industry && <span className="text-red-600 text-xs">{errors.industry}</span>}
        </div>

        {/* Role */}
        <div className="flex flex-col gap-1">
          <Label>Role</Label>
          <Input
            placeholder="e.g. Frontend Developer"
            className="bg-white"
            value={form.role}
            onChange={e => handleChange("role", e.target.value)}
            disabled={loading}
          />
          {errors.role && <span className="text-red-600 text-xs">{errors.role}</span>}
        </div>

        {/* Description */}
        <div className="flex flex-col gap-1">
          <Label>Description</Label>
          <Textarea
            placeholder="Job Description"
            value={form.description}
            onChange={e => handleChange("description", e.target.value)}
            className="min-h-[80px] bg-white"
            disabled={loading}
          />
          {errors.description && <span className="text-red-600 text-xs">{errors.description}</span>}
        </div>

        {/* Location */}
        <div className="flex flex-col gap-1">
          <Label>Location</Label>
          <Input
            placeholder="e.g. Remote, New York"
            value={form.location}
            onChange={e => handleChange("location", e.target.value)}
            className="bg-white"
            disabled={loading}
          />
          {errors.location && <span className="text-red-600 text-xs">{errors.location}</span>}
        </div>

        {/* Salary */}
        <div className="flex flex-col gap-1">
          <Label>Salary</Label>
          <Input
            type="number"
            placeholder="e.g. 50000"
            value={form.salary}
            className="bg-white"
            onChange={e => handleChange("salary", e.target.value)}
            disabled={loading}
          />
          {errors.salary && <span className="text-red-600 text-xs">{errors.salary}</span>}
        </div>

        {/* Salary Currency */}
        <div className="flex flex-col gap-1">
          <Label>Currency</Label>
          <Select
            value={form.salaryCurrency}
            onValueChange={val => handleChange("salaryCurrency", val)}
            disabled={loading}
          >
            <SelectTrigger className="!bg-white !w-[30%] !border-gray-200">
              <SelectValue placeholder="Select" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="USD">USD</SelectItem>
              <SelectItem value="EUR">EUR</SelectItem>
              <SelectItem value="PKR">PKR</SelectItem>
              <SelectItem value="INR">INR</SelectItem>
            </SelectContent>
          </Select>
          {errors.salaryCurrency && <span className="text-red-600 text-xs">{errors.salaryCurrency}</span>}
        </div>

        {/* Salary Period - UPDATED TO DROPDOWN */}
        <div className="flex flex-col gap-1">
          <Label>Salary Period</Label>
          <Select
            value={form.salaryPeriod}
            onValueChange={val => handleChange("salaryPeriod", val)}
            disabled={loading}
          >
            <SelectTrigger className="!bg-white !w-[30%] !border-gray-200">
              <SelectValue placeholder="Select period" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="month">Monthly</SelectItem>
              <SelectItem value="year">Yearly</SelectItem>
            </SelectContent>
          </Select>
          {errors.salaryPeriod && <span className="text-red-600 text-xs">{errors.salaryPeriod}</span>}
        </div>

        {/* Education */}
        <div className="flex flex-col gap-1">
          <Label>Education</Label>
          <Input
            placeholder="e.g. Bachelor's in Computer Science"
            value={form.education}
            onChange={e => handleChange("education", e.target.value)}
            className="bg-white"
            disabled={loading}
          />
          {errors.education && <span className="text-red-600 text-xs">{errors.education}</span>}
        </div>

        {/* Skills */}
        <div className="flex flex-col gap-1">
          <Label>Skills</Label>
          <Input
            placeholder="e.g. React, Node.js, SQL (separated by commas)"
            value={form.skills}
            onChange={e => handleChange("skills", e.target.value)}
            className="bg-white"
            disabled={loading}
          />
          {errors.skills && <span className="text-red-600 text-xs">{errors.skills}</span>}
        </div>

        {/* Experience */}
        <div className="flex flex-col gap-1">
          <Label>Experience</Label>
          <Input
            placeholder="e.g. 2+ years"
            value={form.experience}
            className="bg-white"
            onChange={e => handleChange("experience", e.target.value)}
            disabled={loading}
          />
          {errors.experience && <span className="text-red-600 text-xs">{errors.experience}</span>}
        </div>

        <Button 
          type="submit" 
          className="!bg-blue w-[120px] mt-2"
          disabled={loading}
        >
          {loading ? "Submitting..." : "Submit"}
        </Button>
      </form>
    </div>
  );
}