import { useState, useEffect } from "react";
import CandidatesScoreCard from "@/dashboard-components/candidates-score-card";
import CandidateProfileDialog from "@/dashboard-components/candidate-profile-dailog";
import { useRecruiterStore } from "./recruiter-store";
import { useParams } from "react-router-dom";


export default function InitialScreeningPage() {

  const { JobId } = useParams();

  // Use JobId however you need
  const [openProfile, setOpenProfile] = useState<any>(null);
  const candidates = useRecruiterStore((state) => state.candidates);
  const fetchCandidates = useRecruiterStore((state) => state.fetchCandidates);
  const RejectCandidate = useRecruiterStore((state) => state.RejectCandidate);
  const ReferToHr = useRecruiterStore((state) => state.ReferToHr);
  const selectedCandidate = candidates.find(c => c.id === openProfile);
    
  useEffect(() => {
    fetchCandidates();
  }, [fetchCandidates]);


   return (
    <div className="flex flex-row justify-center w-full my-10 gap-4">
      {/* Score Cards */}
      <div
        className={`flex flex-col gap-4 items-start justify-start transition-all duration-300 ${
          openProfile !== null ? "md:w-1/2 w[95%]" : "w-[95%]"
        }`}
      >
            {candidates
      .filter(candidate => String(candidate.jobId) === String(JobId)) // match candidate ID to URL param
      .map((candidate, id) => (
        <CandidatesScoreCard
          key={candidate.id}
          name={candidate.name}
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
          <div className=" hidden sm:flex w-[45%] items-start justify-center">
            <CandidateProfileDialog
              open={openProfile !== null}
              onOpenChange={(open) => !open && setOpenProfile(null)}
              candidate={selectedCandidate}
              onReject={() => {
                 RejectCandidate(String(selectedCandidate?.id), selectedCandidate?.jobId);
                 setOpenProfile(null);
               }}
               referToHr={() => {
                 ReferToHr(String(selectedCandidate?.id), selectedCandidate?.jobId);
                 setOpenProfile(null);
               }}
                />
          </div>
          {/* Mobile: Overlay Dialog */}
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 sm:hidden">
            <div className="w-[95vw] max-h-[95vh] overflow-y-auto">
              <CandidateProfileDialog
                open={openProfile !== null}
                onOpenChange={(open) => !open && setOpenProfile(null)}
                candidate={selectedCandidate}
                onReject={() => {
                 RejectCandidate(String(selectedCandidate?.id), selectedCandidate?.jobId);
                 setOpenProfile(null);
               }}
               referToHr={() => {
                 ReferToHr(String(selectedCandidate?.id), selectedCandidate?.jobId);
                 setOpenProfile(null);
               }}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
}