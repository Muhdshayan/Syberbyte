import { Card } from "@/components/ui/card";
import { Briefcase, Users2, Target, Clock } from "lucide-react";

interface StatCardProps {
  label: string;
  icon: React.ReactNode;
  value: string | number;
  sub: string;
  bold?: boolean;
}

function StatCard({ label, icon, value, sub, bold }: StatCardProps) {
  return (
    <Card className="font-inter-regular w-[90%] md:min-w-[210px] flex-1 max-w-xs p-5 rounded-lg shadow-sm flex flex-col justify-between">
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

interface HrDashboardCardsProps {
  activeJobs: { value: string | number; sub: string };
  totalCandidates: { value: string | number; sub: string };
  interviewsScheduled: { value: string | number; sub: string };
  timeToHire: { value: string | number; sub: string };
}

export default function HrDashboardCards(props: HrDashboardCardsProps) {
  return (
    <div className="flex md:flex-row flex-col justify-center items-center bg-yellow-200  w-full gap-4">
      <StatCard
        label="Active Jobs"
        icon={<Briefcase className="w-5 h-5 ml-2 text-muted-foreground" />}
        value={props.activeJobs.value}
        sub={props.activeJobs.sub}
      />
      <StatCard
        label="Total Candidates"
        icon={<Users2 className="w-5 h-5 ml-2 text-muted-foreground" />}
        value={props.totalCandidates.value}
        sub={props.totalCandidates.sub}
      />
      <StatCard
        label="Interviews Scheduled"
        icon={<Target className="w-5 h-5 ml-2 text-muted-foreground" />}
        value={props.interviewsScheduled.value}
        sub={props.interviewsScheduled.sub}
      />
      <StatCard
        label="Time to Hire"
        icon={<Clock className="w-5 h-5 ml-2 text-muted-foreground" />}
        value={props.timeToHire.value}
        sub={props.timeToHire.sub}
        bold
      />
    </div>
  );
}