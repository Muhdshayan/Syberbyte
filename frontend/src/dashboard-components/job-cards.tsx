import { Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
    CardFooter,
 } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import type { Job } from "../dashboard/RecruiterDashboard/recruiter-store";
import { Upload } from "lucide-react";
import {useState} from "react"
import { BulkUpload } from "./bulk-upload";
import { Pencil, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import EditJobCategoryDialog from "./edit-job-category";
import DeleteJobCategoryDialog from "./delete-job-category";


type JobCardProps = Job & {
  permission: number;
};

export default function JobCards({ permission, ...props }: JobCardProps) {
    let permissions = permission;
    const navigate = useNavigate();
    const [open, setOpen] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

    const skillsArray = Array.isArray(props.skills)
        ? props.skills
        : String(props.skills).split(",").map(s => s.trim()).filter(Boolean);

    return(
        <Card className="w-90% justify-between">
            <CardHeader>
                <CardTitle className="text-xl font-poppins-semibold text-left">{props.role}</CardTitle>
                <CardDescription className="font-inter-regular text-left">{props.description}</CardDescription>
            </CardHeader>
            <CardContent className="!font-inter-regular text-left w-full">
                <div className="flex gap-2 w-full justify-between"><p className="font-inter-bold text-sm">Location:</p><p className="text-secondary text-sm">{props.location}</p></div>
                <div className="flex gap-2 w-full justify-between"><p className="font-inter-bold text-sm">Type</p><p className="text-secondary text-sm">{props.job_type}</p></div>
                <div className="flex gap-2 w-full justify-between"><p className="font-inter-bold text-sm">Education Level</p><p className="text-secondary text-sm">{props.education_level}</p></div>
                <div className="flex gap-2 w-full justify-between"><p className="font-inter-bold text-sm">Salary</p><p className="text-secondary text-sm">{props.salary}{props.salary_currency}/{props.salary_period}</p></div>
                <div className="flex gap-2 w-full justify-between my-2">
                    <p className="font-inter-bold text-sm">Skills</p>
                    <div className="flex flex-wrap gap-1">
                        {skillsArray.map((skill, idx) => (
                            <Badge key={idx} className="bg-green text-white break-words whitespace-normal">{skill}</Badge>
                        ))}
                    </div>
                </div>
                <div className="bg-green rounded-full inline-block text-sm text-white px-3 py-1">{props.date_posted}</div>
            </CardContent>
            <CardFooter className="w-full justify-between">
                {permissions === 3 && (
                    <div className="flex gap-2 mt-2">
                        <button
                            type="button"
                            className="transition-all bg-blue cursor-pointer rounded-lg hover:bg-blue-700 hover:scale-105 text-white p-2"
                            title="Edit"
                            onClick={() => setEditDialogOpen(true)}
                        >
                            <Pencil className="w-5 h-5" />
                        </button>
                        <button
                            type="button"
                            className="transition-all bg-blue cursor-pointer rounded-lg hover:bg-blue-700 hover:scale-105 text-white p-2"
                            title="Delete"
                            onClick={() => setDeleteDialogOpen(true)}
                        >
                            <Trash2 className="w-5 h-5" />
                        </button>
                        {/* Edit Dialog */}
                        <EditJobCategoryDialog
                            open={editDialogOpen}
                            onOpenChange={setEditDialogOpen}
                            job={props}
                            onSave={() => setEditDialogOpen(false)}
                        />
                        {/* Delete Dialog */}
                        <DeleteJobCategoryDialog
                            open={deleteDialogOpen}
                            onOpenChange={setDeleteDialogOpen}
                            onDelete={() => setDeleteDialogOpen(false)}
                        />
                    </div>
                )}
                {permissions === 1 && (
                    <Button 
                        className="!bg-green !text-sm !font-inter-regular"
                        onClick={() => setOpen(true)}
                    >
                        Upload<Upload/>
                    </Button>
                )}
                <Button
                    className="!bg-blue !text-sm !font-inter-regular"
                    onClick={() =>
                        permissions === 1
                            ? navigate(`/dashboard/recruiter/${props.job_id}/Initial-Screening`)
                            : navigate(`/dashboard/hr_manager/${props.job_id}/final-screening`)
                    }
                >
                    View Candidates
                </Button>
                {permissions === 1 && open && (
                    <BulkUpload
                        onClose={() => setOpen(false)}
                        jobId={props.job_id}
                    />
                )}
            </CardFooter>
        </Card>
    )
}