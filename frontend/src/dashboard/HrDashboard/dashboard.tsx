import HrDashboardCards from "@/dashboard-components/hr-dashboard-cards";
import JobCards from "@/dashboard-components/job-cards";
import { useHrStore } from "./hr-store";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../../Login/useAuthStore";

export default function ActiveJobs() {
    const authUser = useAuthStore((state) => state.authUser);
    const navigate = useNavigate();
    const jobs = useHrStore((state) => state.jobs);
    const fetchJobs = useHrStore((state) => state.fetchJobs);
    
    useEffect(() => {
        fetchJobs();
    }, [fetchJobs]);

    const filteredJobs = authUser?.user_id
        ? jobs.filter((job) => job.posted_by === authUser.user_id)
        : [];

    return (
        <div className="flex flex-col mt-5 justify-start items-center w-full ">
            <HrDashboardCards
                activeJobs={{ value: 3, sub: "2+ this week" }}
                totalCandidates={{ value: 1400, sub: "+150 this week" }}
                interviewsScheduled={{ value: 5, sub: "for next 7 days" }}
                timeToHire={{ value: "12 days", sub: "-2 vs last month" }}
            />
            <div className="flex md:w-[95%] w-[90%] items-center justify-between md:my-10 pt-10">
                <h2 className="text-3xl font-poppins-semibold">Active Jobs</h2>
                <Button
                    onClick={() => navigate("/dashboard/hr_manager/add-job")}
                    className="!bg-blue !text-sm">Add Job <Plus /></Button>
            </div>
            <div className="w-[95%] md:my-10  my-2 grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-6">
                {filteredJobs.length > 0 ? (
                    filteredJobs.map((job) => <JobCards key={job.job_id} {...job} permission={authUser?.permission ?? 1} /> )
                ) : (
                    <p className="text-center text-gray-500">No jobs assigned to you.</p>
                )}
            </div>
        </div>
    );
}