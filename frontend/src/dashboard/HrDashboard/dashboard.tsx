import HrDashboardCards from "@/dashboard-components/hr-dashboard-cards";
export default function ActiveJobs() {
    return (
        <div className="flex flex-col mt-5 justify-start h-screen w-full ">
            <HrDashboardCards
                activeJobs={{ value: 3, sub: "2+ this week" }}
                totalCandidates={{ value: 1400, sub: "+150 this week" }}
                interviewsScheduled={{ value: 5, sub: "for next 7 days" }}
                timeToHire={{ value: "12 days", sub: "-2 vs last month" }}
            />
        </div>
    );
}