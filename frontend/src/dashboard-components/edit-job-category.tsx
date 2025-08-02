import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";
import { useState } from "react";
import { useAdminStore } from "@/dashboard/adminDashboard/admin-store";
import { useEffect } from "react";
interface EditJobCategoryDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  job: {
    industry: string;
    role: string;
    experience_level: string;
    skills: string;
    salary: string;
    description?: string;
    job_type?: string;
    education_level?: string;
    location?: string;
    is_active?: boolean;
    assigned_to: number
  };
  onSave: (job: any) => void;
}

export default function EditJobCategoryDialog({
  open,
  onOpenChange,
  job,
  onSave,
}: EditJobCategoryDialogProps) {
  const [form, setForm] = useState({
    ...job,
    skills: Array.isArray(job.skills) ? job.skills.join(", ") : job.skills,
    description: job.description || "",
    job_type: job.job_type || "",
    education_level: job.education_level || "",
    location: job.location || "",
    is_active: job.is_active ?? true,
    assigned_to: job.assigned_to || 0,
  });
  const users = useAdminStore((state) => state.users); // Get users from admin store
  const fetchUsers = useAdminStore((state) => state.fetchUsers); // Get fetchUsers function
  useEffect(() => {
      if (!users || users.length === 0) {
        fetchUsers();
      }
    }, [users, fetchUsers]);
  
    // Filter users to get only recruiters
    const recruiters = users?.filter(user => user.role === "Recruiter") || [];
    console.log("Recruiters:", recruiters); 

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="md:max-w-md md:w-full h-[90vh] overflow-y-auto w-[80%] !font-inter-regular">
        <DialogHeader>
          <DialogTitle className="!font-poppins-semibold">Edit Job</DialogTitle>
          <DialogDescription>
            Make changes to system jobs here. Click save when you're done.
          </DialogDescription>
        </DialogHeader>
        <form
          onSubmit={(e) => {
            e.preventDefault();

            const updatedJob = {
              ...form,
              skills: form.skills
                .split(",")
                .map((skill) => skill.trim())
                .filter((skill) => skill.length > 0),
            };

            onSave(updatedJob);
          }}
          className="space-y-3"
        >
          <div>
            <label className="block text-sm font-medium mb-1">Industry</label>
            <Input
              value={form.industry}
              onChange={(e) => setForm({ ...form, industry: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Role</label>
            <Input
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <Input
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Job description"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Job Type</label>
            <Select
              value={form.job_type}
              onValueChange={(val) => setForm({ ...form, job_type: val })}
            >
              <SelectTrigger className="!bg-white !text-primary !border-gray-200">
                 <SelectValue
                     placeholder="Select job type"
                     // Show capitalized value if selected
                     // fallback to placeholder if not selected
                   >
                     {form.job_type
                       ? form.job_type.charAt(0).toUpperCase() + form.job_type.slice(1)
                       : "Select job type"}
                   </SelectValue>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="onsite">Onsite</SelectItem>
                <SelectItem value="remote">Remote</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Experience Level</label>
            <Input
              value={form.experience_level}
              onChange={(e) => setForm({ ...form, experience_level: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Required Skills</label>
            <Input
              value={form.skills}
              onChange={(e) => setForm({ ...form, skills: e.target.value })}
              placeholder="Comma separated (e.g. Python, SQL, Excel)"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Education Level</label>
            <Input
              value={form.education_level}
              onChange={(e) => setForm({ ...form, education_level: e.target.value })}
              placeholder="e.g. Bachelor's, Master's"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Location</label>
            <Input
              value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
              placeholder="e.g. New York, Remote"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Salary Range</label>
            <Input
              value={form.salary}
              onChange={(e) => setForm({ ...form, salary: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Status</label>
            <Select
              value={form.is_active ? "active" : "inactive"}
              onValueChange={(val) =>
                setForm({ ...form, is_active: val === "active" })
              }
            >
              <SelectTrigger className="!bg-white !text-primary !border-gray-200">
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label>Assign to</label>
            <Select
            value={form.assigned_to.toString()}
            onValueChange={(val) => setForm({ ...form, assigned_to: parseInt(val) })}>
              <SelectTrigger>
                <SelectValue placeholder="select recruiter"/>
              </SelectTrigger>
              <SelectContent>
                {recruiters.length > 0 ? (
                  recruiters.map((recruiter) => (
                    <SelectItem key={recruiter.id} value={recruiter.id.toString()}>
                      {recruiter.name}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItem value="no recruiters" disabled>No recruiters found</SelectItem>
                )}
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button type="submit" className="!bg-green !text-sm">
              Save changes
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}