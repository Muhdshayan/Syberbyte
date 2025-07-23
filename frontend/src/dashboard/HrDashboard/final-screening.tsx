import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, ShieldCheck, Brain, LayoutGrid } from "lucide-react";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { useHrStore } from "./hr-store";
import { useEffect, useState} from "react"; 
import CandidatesScoreCard from "@/dashboard-components/candidates-score-card";
import CandidateProfileDialog from "@/dashboard-components/candidate-profile-dailog";
import {Button} from "@/components/ui/button";
import { useParams } from "react-router-dom";
import { toast } from "sonner";
import { useRecruiterStore } from "../RecruiterDashboard/recruiter-store";
import NoData from "@/dashboard-components/no-jobs";
import Loading from "@/dashboard-components/loading";

const analyticsData = [
  {
    icon: <Users className="w-5 h-5" />,
    title: "Diversity Analytics",
    stats: [
      { value: "38%", label: "Gender Diversity" },
      { value: 27, label: "Average Age" },
      { value: 5, label: "Countries" },
    ],
    alert: "Potential Bias Alert: Name-based bias detected in 2 evaluations",
  },
  {
    icon: <ShieldCheck className="w-5 h-5" />,
    title: "Bias Detection",
    stats: [
      { value: "97%", label: "Fair Evaluation" },
      { value: 1, label: "Raised Flags" },
    ],
    alert: "Potential Bias Alert: Name-based bias detected in 1 evaluation",
  },
  {
    icon: <Brain className="w-5 h-5" />,
    title: "AI Hiring Recommendations",
    stats: [
      { value: 2, label: "Recommended" },
      { value: 1, label: "Further Review" },
      { value: 3, label: "Not Recommended" },
    ],
    alert: "Potential Bias Alert: Name-based bias detected in 1 evaluation",
  },
];

interface Stat {
  value: string | number;
  label: string;
}

interface AnalyticsCardProps {
  icon: React.ReactNode;
  title: string;
  stats: Stat[];
  alert: string;
}

function AnalyticsCard({ icon, title, stats, alert }: AnalyticsCardProps) {
  return (
    <Card className="w-full shadow min-w-[250px]">
      <CardHeader className="flex flex-row items-center gap-2">
        {icon}
        <CardTitle className="text-lg font-semibold break-words">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between text-sm mb-2 flex-wrap gap-2">
          {stats.map((stat, idx) => (
            <div key={idx} className="min-w-[80px] max-w-[110px]">
              <div className="font-bold text-lg break-words">{stat.value}</div>
              <div className="text-muted-foreground text-xs break-words">{stat.label}</div>
            </div>
          ))}
        </div>
        <Badge className="bg-green text-white w-full justify-center py-2 mt-2 break-words whitespace-normal text-xs">
          {alert}
        </Badge>
      </CardContent>
    </Card>
  );
}

export default function FinalScreeningPage() {
  // Fix: Use individual selectors to avoid infinite loops
  const candidates = useHrStore((state) => state.candidates);
  const fetchCandidates = useHrStore((state) => state.fetchCandidates);
    const { JobId } = useParams();
    const [openProfile, setOpenProfile] = useState<any>(null);
    const {
    updateCandidateStatusLocally, 
    editCandidates,
    hasUnsavedChanges,
    changedCandidates,
    resetUnsavedChanges,
    loading,
    } = useHrStore();

  const finalScreeningCandidates = candidates.filter(candidate => 
    candidate.jobId == JobId && candidate.status != "not_selected" && candidate.status != "rejected"
  );


  const selectedCandidate = finalScreeningCandidates.find(c => c.id === openProfile);

    const handleReject = (candidateId: number, jobId: number) => {
      updateCandidateStatusLocally(candidateId, jobId, "rejected_by_hr");
      setOpenProfile(null);
    };
  
    const handleShortlist = (candidateId: number, jobId: number) => {
      updateCandidateStatusLocally(candidateId, jobId, "final_screening");
      setOpenProfile(null);
    };

    const handleSaveChanges = async () => {
        try {
          const changedCandidatesList = candidates.filter(candidate => 
            changedCandidates.has(`${candidate.id}-${candidate.jobId}`)
          );
    
          console.log("Saving changed candidates:", changedCandidatesList);
          await editCandidates(changedCandidatesList);
          resetUnsavedChanges();
          
          toast.success(`Successfully saved ${changedCandidatesList.length} candidate updates`);
        } catch (error) {
          console.error("Error saving changes:", error);
          toast.error("Failed to save changes. Please try again.");
        }
      };

  useEffect(() => {
    fetchCandidates();
  }, [fetchCandidates]);

  return (
    <div className="p-4 w-screen flex flex-col gap-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {analyticsData.map((card) => (
          <AnalyticsCard
            key={card.title}
            icon={card.icon}
            title={card.title}
            stats={card.stats}
            alert={card.alert}
          />
        ))}
      </div>
      
      {/* Comparison Matrix Table */}
      <Card className="w-full shadow">
        <CardHeader className="flex flex-row items-center gap-2 pb-2">
          <LayoutGrid className="w-5 h-5" />
          <CardTitle className="text-lg font-semibold">Comparison Matrix</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="font-semibold">Candidate</TableHead>
                <TableHead className="font-semibold">Technical</TableHead>
                <TableHead className="font-semibold">Experience</TableHead>
                <TableHead className="font-semibold">Cultural</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {finalScreeningCandidates.length > 0 ? (
                finalScreeningCandidates.map((candidate, idx) => (
                  <TableRow key={candidate.id ?? idx}>
                    <TableCell className="font-medium" align="left">{candidate.name}</TableCell>
                    <TableCell align="left">{candidate.breakdown?.technical ?? 'N/A'}</TableCell>
                    <TableCell align="left">{candidate.breakdown?.experience ?? 'N/A'}</TableCell>
                    <TableCell align="left">{candidate.breakdown?.cultural ?? 'N/A'}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-gray-500">
                    No candidates in final screening for Job ID: {JobId}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      <div className="flex flex-col items-end justify-center w-full h-full">
      <Button 
        className={`bg-gradient-to-bl from-green-500 to-blue-500 text-white font-inter-regular mr-9 hover:scale-105 transition-all duration-200 ${
          !hasUnsavedChanges ? 'opacity-50 cursor-not-allowed' : ''
        }`}
        disabled={!hasUnsavedChanges}
        onClick={handleSaveChanges}
      >
        Save Changes {hasUnsavedChanges && changedCandidates ? `(${changedCandidates.size})` : ''}
      </Button>
      
     <div className="flex flex-row justify-center w-full my-10 gap-4">
        {/* Score Cards */}
        <div
          className={`flex flex-col gap-4 items-start justify-start transition-all duration-300 ${
            openProfile !== null ? "md:w-1/2 w-[95%]" : "w-[95%]"
          }`}
        >
          {loading ? (
            // Show Loading component when data is being fetched
            <Loading />
          ) : finalScreeningCandidates.length > 0 ? (
            // Show candidates when data is available
            finalScreeningCandidates.map((candidate) => (
              <CandidatesScoreCard
                key={`${candidate.id}-${candidate.status}`}
                name={candidate.name}
                status={candidate.status}
                score={candidate.score}
                recommendation={candidate.recommendation}
                onViewProfile={() => setOpenProfile(candidate.id)}
              />
            ))
          ) : (
            // Show NoData component when no candidates found
            <NoData title="No candidates assigned to this job." />
          )}
        </div>
        
        {/* Side Dialog */}
        {openProfile !== null && selectedCandidate && (
          <>
            {/* Desktop: Side Card */}
            <div className="hidden relative sm:flex w-[45%] items-start justify-center">
              <CandidateProfileDialog
                open={openProfile !== null}
                onOpenChange={(open) => !open && setOpenProfile(null)}
                candidate={selectedCandidate}
                onReject={() => handleReject(selectedCandidate?.id, selectedCandidate?.jobId)}
                Shortlist={() => handleShortlist(selectedCandidate?.id, selectedCandidate?.jobId)}
              />
            </div>
            {/* Mobile: Overlay Dialog */}
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 sm:hidden">
              <div className="w-[95vw] max-h-[95vh] overflow-y-auto">
                <CandidateProfileDialog
                  open={openProfile !== null}
                  onOpenChange={(open) => !open && setOpenProfile(null)}
                  candidate={selectedCandidate}
                  onReject={() => handleReject(selectedCandidate?.id, selectedCandidate?.jobId)}
                  Shortlist={() => handleShortlist(selectedCandidate?.id, selectedCandidate?.jobId)}
                />
              </div>
            </div>
          </>
        )}
      </div>
    </div>
    </div>
  );
}