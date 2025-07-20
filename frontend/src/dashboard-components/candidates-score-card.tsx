import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface CandidateScoreCardProps {
  name: string;
  score: number;
  recommendation: string;
  onViewProfile?: () => void;
}

export default function CandidatesScoreCard({
  name,
  score,
  recommendation,
  onViewProfile,
}: CandidateScoreCardProps) {
  return (
    <Card className=" w-full p-5 flex flex-col gap-2 shadow-sm">
      <div className="flex justify-between items-center font-inter-regular">
        <span className="text-lg font-poppins-semibold">{name}</span>
        <span className="bg-green text-white rounded-full px-4 py-1 text-sm font-medium">
         {score}/100
        </span>
      </div>
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mt-2 gap-2">
        
        <p className="font-inter-regular text-secondary text-left text-sm">
            <span className="font-inter-medium text-primary text-md mr-2">AI Recommendation:</span>
          {recommendation}</p>
        
        <Button className="!bg-blue !text-sm" onClick={onViewProfile}>
          View Profile
        </Button>
      </div>
    </Card>
  );
}