import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { MoreVertical, Edit, Trash2 } from "lucide-react";
import type { JobCategory } from "@/dashboard/adminDashboard/admin-store";

interface JobCategoryMobTableProps {
  jobs: JobCategory[];
  onEdit?: (job: JobCategory) => void;
  onDelete?: (job: JobCategory) => void;
}

export default function JobCategoryMobTable({ jobs, onEdit, onDelete }: JobCategoryMobTableProps) {
  return (
    <>
      {jobs.map((item, idx) => (
        <Card key={idx} className="p-4 w-full flex flex-col gap-2 shadow-md relative">
          <div className="flex justify-between items-center mb-2">
           
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <MoreVertical className="w-5 h-5 cursor-pointer" />
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem className="justify-between" onClick={() => onEdit?.(item)}>
                  Edit Job <Edit className="w-5 h-5 text-green-600" />
                </DropdownMenuItem>
                <DropdownMenuItem className="justify-between text-red-600" onClick={() => onDelete?.(item)}>
                  Delete Job <Trash2 className="w-5 h-5" />
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
           <div className="flex w-full justify-between items-center">
              <span className="block text-xs text-muted-foreground">Industry</span>
              <span className="block text-sm font-medium">{item.industry}</span>
            </div>
          <div className="flex justify-between">
            <span className="text-xs text-muted-foreground">Role</span>
            <span className="text-sm font-medium">{item.role}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-xs text-muted-foreground">Status</span>
            <Badge className={`text-white ${item.is_active ? "bg-green" : "bg-red-500"}`}>
                        {item.is_active ? "Active" : "Inactive"}
                      </Badge>
          </div>
          <div className="flex justify-between">
            <span className="text-xs text-muted-foreground">Education</span>
            <span className="text-sm font-medium">{item.education_level}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-xs text-muted-foreground">Experience</span>
            <span className="text-sm font-medium">{item.experience_level}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-xs text-muted-foreground">Salary</span>
            <span className="text-sm font-medium">{item.salary}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-xs text-muted-foreground">Location</span>
            <span className="text-sm font-medium">{item.location}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-xs text-muted-foreground">Job</span>
            <span className="text-sm font-medium">{item.job_type}</span>
          </div>
          
          <div className="flex w-full justify-between item-start">
            <span className="text-xs text-muted-foreground text-left">Required Skills</span>
            <div className="flex flex-wrap gap-2 justify-end">
                {(Array.isArray(item.skills) ? item.skills : String(item.skills).split(",").map(s => s.trim())).map((skill, i) => (
                  <Badge key={i} className="bg-green text-white">{skill}</Badge>
                ))}
            </div>
          </div>
        </Card>
      ))}
    </>
  );
}