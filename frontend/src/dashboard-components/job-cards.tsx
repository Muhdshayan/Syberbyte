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
import {useAuthStore} from "../Login/useAuthStore"
import { Pencil, Trash2 } from "lucide-react";

export default function JobCards(props:Job) {
    const authUser = useAuthStore((state) => state.authUser);
    let permission = 1; // Change to 1 to test upload
    
    const navigate = useNavigate();
    const [open, setOpen] = useState(false);
    return(
            <Card className="w-90% justify-between">
                <CardHeader>
                    <CardTitle className="text-xl font-poppins-semibold text-left">{props.title}</CardTitle>
                    <CardDescription className="font-inter-regular text-left">{props.description}</CardDescription>
                </CardHeader>
                <CardContent className="!font-inter-regular text-left">
                    <div className="flex gap-2"><p className="font-inter-bold text-sm">Location:</p><p className="text-secondary text-sm">{props.location}</p></div>
                    <div className="flex gap-2"><p className="font-inter-bold text-sm">Type</p><p className="text-secondary text-sm">{props.type}</p></div>
                    <div className="flex gap-2"><p className="font-inter-bold text-sm">Salary</p><p className="text-secondary text-sm">{props.salary}</p></div>
                    <div className="bg-green rounded-full inline-block text-sm text-white px-3 py-1 mt-2">Posted on: MM/DD/YY</div>
                    
                </CardContent>
                <CardFooter className="w-full justify-between">
                    {permission === 3 && (
                        <div className="flex gap-2 mt-2">
                                <Pencil className="w-5 h-5"/>
                                <Trash2 className="w-5 h-5"/>
                        </div>
                    )}
                    {permission === 1 && (
                        <Button 
                        className="!bg-green !text-sm !font-inter-regular"
                        onClick={() => setOpen(true)}>Upload<Upload/></Button>
                    )}
                    
                   <Button className="!bg-blue !text-sm !font-inter-regular" onClick={() => navigate(`/dashboard/recruiter/${props.id}/Initial-Screening`)}>View Candidates</Button>
                   {permission === 1 && open &&(
                        <BulkUpload
                            onClose={() => setOpen(false)}
                            jobId={props.id}
                        />
                    )}
                </CardFooter>
            </Card>
    )
}