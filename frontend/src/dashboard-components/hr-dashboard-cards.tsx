import { Card } from "@/components/ui/card";
import { Briefcase, Users2, Target, Clock } from "lucide-react";
import { useHrStore } from "../dashboard/HrDashboard/hr-store";
import { useAuthStore } from "../Login/useAuthStore";
import { useRecruiterStore } from "../dashboard/RecruiterDashboard/recruiter-store";
import { useEffect } from "react";


interface StatCardProps {
  label: string;
  icon: React.ReactNode;
  value: string | number;
  sub: string;
  bold?: boolean;
}

function StatCard({ label, icon, value, sub, bold }: StatCardProps) {
  return (
    <Card className="font-inter-regular w-[95%] md:min-w-[210px] flex-1 p-5 rounded-lg shadow-sm flex flex-col justify-between">
      <div className="flex items-center justify-between mb-2">
        <span className="font-poppins-semibold text-base">{label}</span>
        {icon}
      </div>
      <div className="flex items-end justify-between">
        <span className={`text-2xl font-poppins-semibold ${bold ? "font-bold" : ""}`}>
          {value}
        </span>
        <span className="text-xs text-muted-foreground text-right ml-2">{sub}</span>
      </div>
    </Card>
  );
}

export default function HrDashboardCards() {
  const fetchCandidates = useRecruiterStore((state) => state.fetchCandidates);
  const candidates = useRecruiterStore((state) => state.candidates);
  const authUser = useAuthStore((state) => state.authUser);
  const jobs = useHrStore((state) => state.jobs);
  const fetchJobs = useHrStore((state) => state.fetchJobs);

  useEffect(() => {
    fetchJobs();
    fetchCandidates();
  }, [fetchJobs, fetchCandidates]);

  const filteredJobs = authUser?.user_id
    ? jobs.filter((job) => job.posted_by === authUser.user_id)
    : [];

  const jobIds = filteredJobs.map((job) => job.job_id);

  const candidatesForMyJobs = candidates.filter((c) =>
    jobIds.includes(c.jobId)
  );

  const activeJobsCount = filteredJobs.filter((job) => job.is_active).length;
  const totalCandidatesCount = candidatesForMyJobs.length;
  const initialScreenedCount = candidatesForMyJobs.filter(
    (c) => c.status === "initial_screening"
  ).length;
  const finalScreenedCount = candidatesForMyJobs.filter(
    (c) => c.status === "final_screening"
  ).length;

  return (
    <div className="flex md:flex-row flex-col justify-center items-center w-[98%] gap-4 ">
      <StatCard
        label="Active Jobs"
        icon={<Briefcase className="w-5 h-5 ml-2 text-muted-foreground" />}
        value={activeJobsCount}
        sub="active listings"
      />
      <StatCard
        label="Total Candidates"
        icon={<Users2 className="w-5 h-5 ml-2 text-muted-foreground" />}
        value={totalCandidatesCount}
        sub="across all jobs"
      />
      <StatCard
        label="Initial Screened"
        icon={<Target className="w-5 h-5 ml-2 text-muted-foreground" />}
        value={initialScreenedCount}
        sub="initial stage"
      />
      <StatCard
        label="Final Screened"
        icon={<Clock className="w-5 h-5 ml-2 text-muted-foreground" />}
        value={finalScreenedCount}
        sub="final stage"
        bold
      />
    </div>
  );
}
