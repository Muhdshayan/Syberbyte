import JobCards from "@/dashboard-components/job-cards";
import { useEffect } from "react";
import { useRecruiterStore } from "./recruiter-store";




export default function ViewCandidates() {
  const jobs = useRecruiterStore((state) => state.jobs);
  const fetchJobs = useRecruiterStore((state) => state.fetchJobs);

  useEffect(() => {
          fetchJobs();
      }, [fetchJobs]);
      console.log("fetched jobs",jobs);
    
    return (
        <div className="flex flex-col items-center justify-start h-auto w-full py-20 px-10">
            <div className="w-full flex justify-between items-center">
                <h2 className="text-3xl font-poppins-semibold mb-6">View Candidates</h2>
            </div>
            <div className="w-full grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1 gap-6">
               {jobs.map(job => (
                <JobCards key={job.id} {...job} />
                ))}
            </div>
        </div>
    );
}