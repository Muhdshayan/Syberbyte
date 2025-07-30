import HrDashboardCards from "@/dashboard-components/hr-dashboard-cards";
import JobCards from "@/dashboard-components/job-cards";
import NoData from "@/dashboard-components/no-jobs";
import Loading from "@/dashboard-components/loading";
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
    const loading = useHrStore((state) => state.loading);
    
    useEffect(() => {
        fetchJobs();
    }, [fetchJobs]);

    const filteredJobs = authUser?.user_id
        ? jobs.filter((job) => job.posted_by === authUser.user_id)
        : [];

    return (
        <div className="flex flex-col mt-5 justify-start items-center w-full ">
            <HrDashboardCards/>
            <div className="flex md:w-[98%] w-[90%] items-center justify-between py-4">
                <h2 className="text-3xl font-poppins-semibold">Active Jobs</h2>
                <Button
                    onClick={() => navigate("/dashboard/hr_manager/add-job")}
                    className="!bg-blue !text-sm">Add Job <Plus /></Button>
            </div>
            <div className="w-[98%] md:mb-3 mb-2 grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-6">
                {loading ? (
                    // Show Loading component when data is being fetched
                    <div className="col-span-full">
                        <Loading />
                    </div>
                ) : filteredJobs.length > 0 ? (
                    // Show job cards when data is available
                    filteredJobs.map((job) => (
                        <JobCards 
                            key={job.job_id} 
                            {...job} 
                            permission={authUser?.permission ?? 1} 
                        />
                    ))
                ) : (
                    // Show NoData component when no jobs are found
                    <div className="col-span-full">
                        <NoData 
                            title="No Jobs Created" 
                            subtitle="You haven't created any jobs yet. Click 'Add Job' to get started."
                        />
                    </div>
                )}
            </div>
        </div>
    );
}