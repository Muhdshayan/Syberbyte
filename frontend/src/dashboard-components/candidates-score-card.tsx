import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface CandidateScoreCardProps {
  name: string;
  score: number;
  recommendation: string;
  status: string;
  onViewProfile?: () => void;
}

export default function CandidatesScoreCard({
  name,
  score,
  recommendation,
  status,
  onViewProfile,
}: CandidateScoreCardProps) {


function formatStatus(status: string) {
    if (status.toLowerCase() === "initial_screening") {
      return "Suggested by Recruiter";
    }
    return status
      .replace(/_/g, " ") // replace underscores with spaces
      .replace(/\b\w/g, (char) => char.toUpperCase()); // capitalize first letter of each word
  }

  const getBadgeColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'rejected':
        return '!bg-red-500';
      case 'final_screening':
        return '!bg-green';
      case 'initial_screening':
        return '!bg-blue';
      case 'rejected_by_hr':
        return '!bg-red-600';
      default:
        return '!bg-secondary';
    }
  };

  return (

  <Card className="w-full p-5 flex flex-col gap-2 shadow-sm hover:shadow-lg hover:scale-[1.02] transition-all duration-300 cursor-pointer">
    <div className="flex justify-between gap-2 items-center font-inter-regular">
      <div className="flex items-center gap-2"> {/* Changed from item-start to items-center */}
        <span className="text-lg text-left font-poppins-semibold">{name}</span>
        <Badge className={`${getBadgeColor(status)} !text-white !text-sm transition-colors self-center h-fit`}>
          {formatStatus(status)}
        </Badge>
      </div>
      <span className="bg-green text-white rounded-full px-4 py-1 text-sm font-medium transition-colors hover:bg-green-600">
       {score}/100
      </span>
    </div>
    <div className="flex flex-col md:flex-row md:items-center md:justify-between mt-2 gap-2">
      <p className="font-inter-regular text-secondary text-left text-sm">
        <span className="font-inter-medium text-primary text-md mr-2">AI Recommendation:</span>
        {recommendation}
      </p>
      
      <Button 
      
        className="!bg-blue !text-sm hover:!bg-blue-700 hover:scale-105 transition-all duration-200" 
        onClick={onViewProfile}
      >
        View Profile
      </Button>
    </div>
  </Card>

  );
}