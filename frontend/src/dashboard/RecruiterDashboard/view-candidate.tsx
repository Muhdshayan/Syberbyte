import { useState } from "react";
import CandidatesScoreCard from "@/dashboard-components/candidates-score-card";
import CandidateProfileDialog from "@/dashboard-components/candidate-profile-dailog";

interface Candidate {
  name: string;
  score: number;
  recommendation: string;
  role: string;
  experience: string;
  breakdown: {
    technical: number;
    experience: number;
    cultural: number;
  };
  summary: string;
  skills: string[];
  experienceList: {
    title: string;
    company: string;
    duration: string;
    location: string;
    description: string;
  }[];
}

const candidates: Candidate[] = [
  {
    name: "1",
    score: 92,
    recommendation: "Strong hire - Excellent technical skills and cultural fit",
    role: "Frontend Developer",
    experience: "Mid-Level (2-4 years)",
    breakdown: { technical: 98, experience: 95, cultural: 85 },
    summary:
      "Experienced Full Stack Developer with 4.5+ years of hands-on experience in designing, developing, and deploying scalable web applications. Proficient in both frontend and backend technologies with a strong focus on React.js, Node.js, and cloud-native solutions. Passionate about building user-centric products, improving performance, and collaborating in agile teams.",
    skills: ["Javascript", "MongoDB", "AWS", "Reactjs", "Nodejs"],
    experienceList: [
      {
        title: "Software Engineer",
        company: "VibeTech Solutions",
        duration: "June 2021 – Present",
        location: "Karachi (Remote)",
        description:
          "Full Stack Developer with 4.5+ years of experience building scalable web applications using React.js, Node.js, and cloud technologies",
      },
    ],
  },
  {
    name: "2",
    score: 85,
    recommendation: "Hire - Good technical background, needs minor upskilling.",
    role: "Backend Developer",
    experience: "Mid-Level (2-4 years)",
    breakdown: { technical: 90, experience: 88, cultural: 80 },
    summary:
      "Backend developer with strong Node.js and SQL skills. Good at building APIs and optimizing performance.",
    skills: ["Node.js", "SQL", "Express", "Docker"],
    experienceList: [
      {
        title: "Backend Developer",
        company: "DataSoft",
        duration: "Jan 2022 – Present",
        location: "Remote",
        description:
          "Developed RESTful APIs and managed database integrations for multiple SaaS products.",
      },
    ],
  },
  {
    name: "3",
    score: 78,
    recommendation: "Consider - Average skills, but shows potential for growth.",
    role: "UI/UX Designer",
    experience: "Junior (1-2 years)",
    breakdown: { technical: 75, experience: 70, cultural: 80 },
    summary:
      "Creative UI/UX designer with a passion for user-centered design and improving digital experiences.",
    skills: ["Figma", "Sketch", "Adobe XD"],
    experienceList: [
      {
        title: "UI/UX Designer",
        company: "Designify",
        duration: "Mar 2023 – Present",
        location: "Remote",
        description:
          "Worked on mobile and web UI projects for various clients, focusing on usability and accessibility.",
      },
    ],
  },
  {
    name: "4",
    score: 65,
    recommendation: "Weak fit - Lacks some required skills, but good attitude.",
    role: "QA Engineer",
    experience: "Junior (1-2 years)",
    breakdown: { technical: 60, experience: 65, cultural: 70 },
    summary:
      "QA Engineer with experience in manual and automated testing. Good attitude and eager to learn.",
    skills: ["Selenium", "Jest", "Cypress"],
    experienceList: [
      {
        title: "QA Engineer",
        company: "Testify",
        duration: "Feb 2023 – Present",
        location: "Remote",
        description:
          "Performed manual and automated testing for web applications, ensuring quality releases.",
      },
    ],
  },
];

export default function ViewCandidatesJobPage() {
  const [openProfile, setOpenProfile] = useState<null | number>(null);

   return (
    <div className="flex flex-row justify-center w-full mb-8 gap-4">
      {/* Score Cards */}
      <div
        className={`flex flex-col gap-4 items-start justify-start transition-all duration-300 ${
          openProfile !== null ? "md:w-1/2 w[95%]" : "w-[95%]"
        }`}
      >
        {candidates.map((candidate, idx) => (
          <CandidatesScoreCard
            key={idx}
            name={candidate.name}
            score={candidate.score}
            recommendation={candidate.recommendation}
            onViewProfile={() => setOpenProfile(idx)}
          />
        ))}
      </div>
      {/* Side Dialog */}
     {openProfile !== null && (
        <>
          {/* Desktop: Side Card */}
          <div className="hidden sm:flex w-[45%] items-start justify-center">
            <CandidateProfileDialog
              open={openProfile !== null}
              onOpenChange={(open) => !open && setOpenProfile(null)}
              candidate={candidates[openProfile]}
              onReject={() => setOpenProfile(null)}
              onSchedule={() => setOpenProfile(null)}
            />
          </div>
          {/* Mobile: Overlay Dialog */}
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 sm:hidden">
            <div className="w-[95vw] max-h-[95vh] overflow-y-auto">
              <CandidateProfileDialog
                open={openProfile !== null}
                onOpenChange={(open) => !open && setOpenProfile(null)}
                candidate={candidates[openProfile]}
                onReject={() => setOpenProfile(null)}
                onSchedule={() => setOpenProfile(null)}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
}