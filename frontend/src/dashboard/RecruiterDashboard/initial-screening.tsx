import { useState, useEffect } from "react";
import CandidatesScoreCard from "@/dashboard-components/candidates-score-card";
import CandidateProfileDialog from "@/dashboard-components/candidate-profile-dailog";
import { useRecruiterStore } from "./recruiter-store";
import { useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";
import NoData from "@/dashboard-components/no-jobs";
import Loading from "@/dashboard-components/loading";
import { useAuthStore } from "@/Login/useAuthStore";
import { Filter, ChevronDown } from "lucide-react";

export default function InitialScreeningPage() {
  const { JobId } = useParams();
  const [openProfile, setOpenProfile] = useState<any>(null);
  const [selectedFilter, setSelectedFilter] = useState<number | null>(null);
  const {authUser} = useAuthStore();
  console.log(authUser?.permission)

  
  const { 
    candidates, 
    fetchCandidates, 
    updateCandidateStatusLocally, 
    editCandidates,
    hasUnsavedChanges,
    changedCandidates,
    resetUnsavedChanges,
    loading
  } = useRecruiterStore();
  
 // Define the status type
type CandidateStatus = 'initial_screening' | 'not_selected' | 'rejected' | string;

// Filter candidates for this job and exclude final_screening/rejected_by_hr
const jobCandidates = candidates.filter(candidate => 
  candidate.jobId === Number(JobId) && candidate.status != "final_screening" && candidate.status != "rejected_by_hr"
);

// Reusable sorting function
const sortCandidates = (candidates: any[], isFiltered: boolean) => {
  return candidates.sort((a, b) => {
    if (isFiltered) {
      // Filtered: Score first, then status priority for ties
      if (a.score !== b.score) {
        return b.score - a.score;
      }
      // Status priority for equal scores
      const statusPriority: Record<string, number> = { 
        initial_screening: 2, 
        pending: 1,
        rejected: 0
      };
      return (statusPriority[b.status as CandidateStatus] || 0) - (statusPriority[a.status as CandidateStatus] || 0);
    } else {
      // Default: Status priority first, then score
      const statusPriority: Record<string, number> = { 
        initial_screening: 2, 
        pending: 1,
        rejected: 0
      };
      const statusDiff = (statusPriority[b.status as CandidateStatus] || 0) - (statusPriority[a.status as CandidateStatus] || 0);
      return statusDiff !== 0 ? statusDiff : b.score - a.score;
    }
  });
};

// Apply filter and sorting
const filteredCandidates = selectedFilter 
  ? sortCandidates([...jobCandidates], true).slice(0, selectedFilter)
  : sortCandidates([...jobCandidates], false);

const selectedCandidate = filteredCandidates.find(c => c.candidate_id === openProfile);

  const handleFilterSelect = (count: number) => {
    setSelectedFilter(count);
    toast.success(`Showing top ${count} candidates`);
  };

  const clearFilter = () => {
    setSelectedFilter(null);
    toast.success("Filter cleared - showing all candidates");
  };
    
  useEffect(() => {
    fetchCandidates();
  }, [fetchCandidates]);

  // Local update functions that only change status locally
  const handleReject = (candidateId: number, jobId: number) => {
    updateCandidateStatusLocally(candidateId, jobId, "rejected");
    toast.success("Candidate rejected successfully");
    setOpenProfile(null);
  };

  const handleReferToHr = (candidateId: number, jobId: number) => {
    updateCandidateStatusLocally(candidateId, jobId, "initial_screening");
    toast.success("Candidate referred to HR for final screening");
    setOpenProfile(null);
  };

  // Save all changes to server
 const handleSaveChanges = async () => {
    try {
      const changedCandidatesList = candidates.filter(candidate => 
        changedCandidates.has(`${candidate.candidate_id}-${candidate.jobId}`)
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

  return (
    <div className="flex flex-col items-end justify-center w-full h-full p-4">
      <div className="flex flex-row justify-between w-full mt-3 gap-4">
        {/* Filter Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button className="bg-gradient-to-bl from-green to-blue text-white font-inter-regular hover:scale-105 gap-2">
              <Filter className="w-4 h-4" />
              Filter
              {selectedFilter && (
                <Badge className="bg-white text-blue-600 ml-1">
                  Top {selectedFilter}
                </Badge>
              )}
              <ChevronDown className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-48">
            <DropdownMenuItem onClick={() => handleFilterSelect(5)}>
              Top 5 Candidates
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleFilterSelect(10)}>
              Top 10 Candidates
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleFilterSelect(15)}>
              Top 15 Candidates
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleFilterSelect(30)}>
              Top 30 Candidates
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={clearFilter} className="text-gray-600">
              Show All Candidates
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <Button 
          className={`bg-gradient-to-bl from-green-500 to-blue-500 text-white font-inter-regular hover:scale-105 transition-all duration-200 ${
            !hasUnsavedChanges ? 'opacity-50 cursor-not-allowed' : ''
          }`}
          disabled={!hasUnsavedChanges}
          onClick={handleSaveChanges}
        >
          Save Changes {hasUnsavedChanges && changedCandidates ? `(${changedCandidates.size})` : ''}
        </Button>
      </div>
      
     <div className="flex flex-row justify-center w-full mb-10 mt-3 gap-4 sticky bottom-7">
        {/* Score Cards */}
        <div
          className={`flex flex-col gap-4 items-start justify-start transition-all duration-300 ${
            openProfile !== null ? "w-[50%] " : "w-full"
          }`}
        >
          {loading ? (
            // Show Loading component when data is being fetched
            <Loading />
          ) : filteredCandidates.length > 0 ? (
            // Show filtered candidates when data is available
            filteredCandidates.map((candidate) => (
              <CandidatesScoreCard
                key={`${candidate.candidate_id}-${candidate.status}`}
                name={candidate.name}
                status={candidate.status}
                score={candidate.score}
                recommendation={candidate.recommendation}
                onViewProfile={() => setOpenProfile(candidate.candidate_id)}
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
            <div className="hidden sm:flex w-[60%] items-start justify-center">
              <CandidateProfileDialog
                open={openProfile !== null}
                onOpenChange={(open) => !open && setOpenProfile(null)}
                candidate={selectedCandidate}
                onReject={() => handleReject(selectedCandidate?.candidate_id, selectedCandidate?.jobId)}
                referToHr={() => handleReferToHr(selectedCandidate?.candidate_id, selectedCandidate?.jobId)}
              />
            </div>
            {/* Mobile: Overlay Dialog */}
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 sm:hidden">
              <div className="w-[95vw] max-h-[95vh] overflow-y-auto">
                <CandidateProfileDialog
                  open={openProfile !== null}
                  onOpenChange={(open) => !open && setOpenProfile(null)}
                  candidate={selectedCandidate}
                  onReject={() => handleReject(selectedCandidate?.candidate_id, selectedCandidate?.jobId)}
                  referToHr={() => handleReferToHr(selectedCandidate?.candidate_id, selectedCandidate?.jobId)}
                />
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}