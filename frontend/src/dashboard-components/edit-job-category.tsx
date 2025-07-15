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
import { useState } from "react";

interface EditJobCategoryDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  job: {
    industry: string;
    role: string;
    experience: string;
    skills: string[];
    salary: string;
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
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="md:max-w-md md:w-full w-[80%] !font-inter-regular">
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
            <label className="block text-sm font-medium mb-1">Experience Level</label>
            <Input
              value={form.experience}
              onChange={(e) => setForm({ ...form, experience: e.target.value })}
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
            <label className="block text-sm font-medium mb-1">Salary Range</label>
            <Input
              value={form.salary}
              onChange={(e) => setForm({ ...form, salary: e.target.value })}
              required
            />
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
