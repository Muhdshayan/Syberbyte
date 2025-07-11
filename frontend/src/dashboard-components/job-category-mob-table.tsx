import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { MoreVertical, Edit, Trash2 } from "lucide-react";
import { useState } from "react";
import DeleteJobCategoryDialog from "./delete-job-category";
import EditJobCategoryDialog from "./edit-job-category";

interface JobCategoryMobTableProps {
  job: {
    industry: string;
    role: string;
    experience: string;
    salary: string;
    skills: string[];
  };
  onEdit?: () => void;
  onDelete?: () => void;
}

export default function JobCategoryMobTable({ job, onEdit, onDelete }: JobCategoryMobTableProps) {
    const [editJob, setEditJob] = useState(null);
    const [deleteJob, setDeleteJob] = useState(null);
    return (
    <Card className="p-4 w-full flex flex-col gap-2 shadow-md relative">
      <div className="flex justify-between">
        <span className="text-xs text-muted-foreground">Industry</span>
        <span className="text-sm font-medium">{job.industry}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-xs text-muted-foreground">Role</span>
        <span className="text-sm font-medium">{job.role}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-xs text-muted-foreground">Experience</span>
        <span className="text-sm font-medium">{job.experience}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-xs text-muted-foreground">Salary</span>
        <span className="text-sm font-medium">{job.salary}</span>
      </div>
      <div className="flex gap-2 justify-between">
        <span className=" text-left text-xs text-muted-foreground">Required Skills</span>
        <div className="flex justify-end flex-wrap gap-2 mt-1">
          {job.skills.map((skill, i) => (
            <Badge key={i} className="bg-green text-white">{skill}</Badge>
          ))}
        </div>
      </div>
      <div className="">
        <DropdownMenu>
          <DropdownMenuTrigger asChild >
              <MoreVertical className="w-5 h-5" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
           <DropdownMenuItem className="justify-between" onClick={onEdit}>
              Edit Job <Edit className="w-5 h-5 text-green-600" />
            </DropdownMenuItem>
            <DropdownMenuItem className="justify-between text-red-600" onClick={onDelete}>
              Delete Job <Trash2 className="w-5 h-5" />
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </Card>
  );
}