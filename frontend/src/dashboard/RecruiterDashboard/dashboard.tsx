import JobCards from "@/dashboard-components/job-cards";


export interface Job {
  id: number;           // unique identifier
  title: string;        // job title
  description: string;  // short pitch / overview
  location: string;     // city or "Remote"
  type: "Full-time" | "Part-time" | "Contract" | "Internship";
  salary: string;       // formatted, e.g. "$60,000/year"
  postedOn: string;     // MM/DD/YY  (store as ISO string if you need real dates)
}
export const jobs: Job[] = [
  {
    id: 1,
    title: "Software Engineer",
    description:
      "We're looking for a passionate Frontend Developer to join our product team and bring designs to life using React.js. You'll work closely with designers and backend engineers to build fast, intuitive, and responsive web apps.",
    location: "Remote",
    type: "Full-time",
    salary: "$60,000/year",
    postedOn: "07/01/25",
  },
  {
    id: 2,
    title: "Backend Developer",
    description:
      "Join our backend team to help build scalable APIs using Node.js and PostgreSQL. You'll design robust systems and optimize performance.",
    location: "Lahore, PK",
    type: "Contract",
    salary: "$45/hour",
    postedOn: "06/29/25",
  },
  {
    id: 3,
    title: "UI/UX Designer",
    description:
      "We're seeking a creative UI/UX designer to craft intuitive interfaces and deliver amazing user experiences across all devices.",
    location: "Remote",
    type: "Internship",
    salary: "$1,000/month",
    postedOn: "07/03/25",
  },
  {
    id: 4,
    title: "DevOps Engineer",
    description:
      "You will manage CI/CD pipelines, monitor system performance, and ensure high availability of services using AWS and Docker.",
    location: "Karachi, PK",
    type: "Full-time",
    salary: "$75,000/year",
    postedOn: "06/28/25",
  },
  {
    id: 5,
    title: "AI/ML Engineer",
    description:
      "Work on cutting‑edge AI projects including NLP, recommendation systems, and predictive analytics. Experience with Python and TensorFlow required.",
    location: "Hybrid (Islamabad)",
    type: "Full-time",
    salary: "$90,000/year",
    postedOn: "06/27/25",
  },
] as const;
export default function ViewCandidates() {
    
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