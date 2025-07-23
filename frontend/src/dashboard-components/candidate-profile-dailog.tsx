import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import type { Candidate } from "@/dashboard/RecruiterDashboard/recruiter-store"; // Adjust path as needed
import { useAuthStore } from "@/Login/useAuthStore";

interface CandidateProfileCardProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  candidate: Candidate;
  
  onReject?: () => void;
  referToHr?: () => void;
  Shortlist?: () => void;
}

export default function CandidateProfileCard({
  open,
  onOpenChange,
  candidate,
  onReject,
  referToHr,
  Shortlist
}: CandidateProfileCardProps) {
  const permission = useAuthStore((state) => state.authUser?.permission);
  
  if (!open) return null;
  
  return (
    <Card className="w-full shadow-lg p-6 relative animate-in fade-in font-inter-regular">
      <div className="flex justify-between items-start mb-2">
        <div>
          <div className="text-2xl font-poppins-semibold">{candidate.name}</div>
        </div>
        <X className="w-5 h-5" onClick={() => onOpenChange(false)}/>
      </div>
      <div className="flex flex-col gap-1 mt-2">
        <div className="flex items-center gap-2">
          <span className="font-inter-semibold">{candidate.role}</span>
          <span className="text-xs text-muted-foreground">{candidate.experience}</span>
        </div>
        <div className="flex items-center gap-2 mt-1">
          <span className="font-inter-semibold">Match score</span>
          <span className="bg-green text-white rounded-full px-3 py-1 text-sm font-medium">
            {candidate.score}%
          </span>
        </div>
      </div>
      {/* Match Confidence Breakdown */}
      <div className="rounded-xl p-4 my-4 bg-gradient-to-br from-green to-blue">
        <div className="flex flex-col gap-2 text-white">
          <div className="flex items-center md:gap-3 gap-1">
             <span className="md:w-40">Technical skills</span>
             <div className="flex-1 mx-2">
               <Progress value={candidate.breakdown.technical} className="h-2 bg-white/40" />
             </div>
             <span className="w-10 text-right">{candidate.breakdown.technical}%</span>
           </div>
           {/* Experience Level */}
           <div className="flex items-center md:gap-3 gap-1">
             <span className="md:w-40">Experience Level</span>
             <div className="flex-1 mx-2">
               <Progress value={candidate.breakdown.experience} className="h-2 bg-white/40" />
             </div>
             <span className="w-10 text-right">{candidate.breakdown.experience}%</span>
           </div>
           {/* Cultural Fit */}
           <div className="flex items-center md:gap-3 gap-1">
             <span className="md:w-40">Cultural Fit</span>
             <div className="flex-1 mx-2">
               <Progress value={candidate.breakdown.cultural} className="h-2 bg-white/40" />
             </div>
             <span className="w-10 text-right">{candidate.breakdown.cultural}%</span>
           </div>
        </div>
      </div>
      {/* Professional Summary */}
      <div className="mt-2 text-left">
        <div className="font-inter-semibold mb-1">Professional Summary</div>
        <div className="text-muted-foreground text-sm">{candidate.summary}</div>
      </div>
      {/* Technical Skills */}
      <div className="mt-3 text-left">
        <div className="font-inter-semibold mb-1">Technical skills</div>
        <div className="flex flex-wrap gap-2">
          {(Array.isArray(candidate.skills)
             ? candidate.skills
             : String(candidate.skills).split(",").map(s => s.trim())
           ).map((skill, i) => (
             <Badge key={i} className="bg-green text-white">{skill}</Badge>
           ))}
        </div>
      </div>
      {/* Experience */}
      <div className="mt-3 text-left">
        <div className="font-inter-semibold mb-1">Experience</div>
        <div className="flex flex-col gap-2">
          {candidate.experienceList.map((exp, i) => (
            <div key={i}>
              <div className="font-medium">{exp.title} | {exp.company}</div>
              <div className="text-xs text-muted-foreground">{exp.duration} | {exp.location}</div>
              <div className="text-sm">{exp.description}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="flex justify-between gap-2 mt-6">
        <Button className="!bg-red-500 !text-sm" onClick={onReject}>
          Reject
        </Button>
        
        {permission === 1 ? (
          <Button className="!bg-blue !text-sm" onClick={referToHr}>
            Refer to HR
          </Button>
        ) : (
          <Button className="!bg-green !text-sm" onClick={Shortlist}>
            Shortlist
          </Button>
        )}
      </div>
    </Card>
  );
}