import JobCards from "@/dashboard-components/job-cards";
import { useEffect } from "react";
import { useRecruiterStore } from "./recruiter-store";
import { useAuthStore } from "../../Login/useAuthStore";
import NoData from "@/dashboard-components/no-jobs";
import Loading from "@/dashboard-components/loading";

export default function ViewCandidates() {
  const authUser = useAuthStore((state) => state.authUser);
  const jobs = useRecruiterStore((state) => state.jobs);
  const fetchJobs = useRecruiterStore((state) => state.fetchJobs);
  const loading = useRecruiterStore((state) => state.loading); // Add loading state

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const filteredJobs = authUser?.user_id
    ? jobs.filter((job) => job.assigned_to === authUser.user_id)
    : [];
  
  console.log(filteredJobs);

  return (
    <div className="flex flex-col items-center justify-start h-auto w-full pt-4 pb-10 px-4">
      <div className="w-full flex justify-between items-center">
        <h2 className="text-3xl font-poppins-semibold mb-6">View Candidates</h2>
      </div>
      
      <div className="w-full grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-6">
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
              title="No Jobs Assigned" 
              subtitle="You currently have no jobs assigned to you."
            />
          </div>
        )}
      </div>
    </div>
  );
}