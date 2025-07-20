import JobCards from "@/dashboard-components/job-cards";
import { useEffect } from "react";
import { useRecruiterStore } from "./recruiter-store";
import { useAuthStore } from "../../Login/useAuthStore";

export default function ViewCandidates() {
  const authUser = useAuthStore((state) => state.authUser);
  const jobs = useRecruiterStore((state) => state.jobs);
  const fetchJobs = useRecruiterStore((state) => state.fetchJobs);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const filteredJobs = authUser?.user_id
    ? jobs.filter((job) => job.assigned_to === authUser.user_id)
    : [];
  console.log(filteredJobs)
  return (
    <div className="flex flex-col items-center justify-start h-auto w-full py-20 px-10">
      <div className="w-full flex justify-between items-center">
        <h2 className="text-3xl font-poppins-semibold mb-6">View Candidates</h2>
      </div>
      <div className="w-full grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-6">
        {filteredJobs.length > 0 ? (
          filteredJobs.map((job) => <JobCards key={job.job_id} {...job} permission={authUser?.permission ?? 1}/>)
        ) : (
          <p className="text-center text-gray-500">No jobs assigned to you.</p>
        )}
      </div>
    </div>
  );
}