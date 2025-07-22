import { useState, useEffect } from "react";
import CandidatesScoreCard from "@/dashboard-components/candidates-score-card";
import CandidateProfileDialog from "@/dashboard-components/candidate-profile-dailog";
import { useRecruiterStore } from "./recruiter-store";
import { useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export default function InitialScreeningPage() {
  const { JobId } = useParams();
  const [openProfile, setOpenProfile] = useState<any>(null);
  
  const { 
    candidates, 
    fetchCandidates, 
    updateCandidateStatusLocally, 
    saveChangesToServer, 
    hasUnsavedChanges,
    changedCandidates,
  } = useRecruiterStore();
  
  // Simple filtering: only candidates matching current job ID
  const jobCandidates = candidates.filter(candidate => 
    candidate.jobId === Number(JobId)
  );
  
  const selectedCandidate = jobCandidates.find(c => c.id === openProfile);
    
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
    updateCandidateStatusLocally(candidateId, jobId, "final_screening");
    toast.success("Candidate referred to HR for final screening");
    setOpenProfile(null);
  };

  // Save all changes to server
  const handleSaveChanges = async () => {
    await saveChangesToServer();
  };

  return (
    <div className="flex flex-col items-end justify-center w-full h-full p-4">
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
          {jobCandidates.map((candidate) => (
            <CandidatesScoreCard
              key={`${candidate.id}-${candidate.status}`}
              name={candidate.name}
              status={candidate.status}
              score={candidate.score}
              recommendation={candidate.recommendation}
              onViewProfile={() => setOpenProfile(candidate.id)}
            />
          ))}
        </div>
        
        {/* Side Dialog */}
        {openProfile !== null && selectedCandidate && (
          <>
            {/* Desktop: Side Card */}
            <div className="hidden sm:flex w-[45%] items-start justify-center">
              <CandidateProfileDialog
                open={openProfile !== null}
                onOpenChange={(open) => !open && setOpenProfile(null)}
                candidate={selectedCandidate}
                onReject={() => handleReject(selectedCandidate?.id, selectedCandidate?.jobId)}
                referToHr={() => handleReferToHr(selectedCandidate?.id, selectedCandidate?.jobId)}
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
                  referToHr={() => handleReferToHr(selectedCandidate?.id, selectedCandidate?.jobId)}
                />
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}