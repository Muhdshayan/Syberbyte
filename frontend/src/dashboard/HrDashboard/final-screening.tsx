import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LayoutGrid } from "lucide-react";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { useHrStore } from "./hr-store";
import { useEffect, useState } from "react";
import CandidatesScoreCard from "@/dashboard-components/candidates-score-card";
import CandidateProfileDialog from "@/dashboard-components/candidate-profile-dailog";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { useParams } from "react-router-dom";
import { toast } from "sonner";
import NoData from "@/dashboard-components/no-jobs";
import Loading from "@/dashboard-components/loading";
import { Filter, ChevronDown } from "lucide-react";

export default function FinalScreeningPage() {
  // Fix: Use individual selectors to avoid infinite loops
  const candidates = useHrStore((state) => state.candidates);
  const fetchCandidates = useHrStore((state) => state.fetchCandidates);
  const { JobId } = useParams();
  const [openProfile, setOpenProfile] = useState<any>(null);
  const [selectedFilter, setSelectedFilter] = useState<number | null>(null);

  const {
    updateCandidateStatusLocally,
    editCandidates,
    hasUnsavedChanges,
    changedCandidates,
    resetUnsavedChanges,
    generateExcelReport,
    loading,
  } = useHrStore();
  type CandidateStatus = 'final_screening' | 'initial_screening' | 'rejected_by_hr' | string;

  const finalScreeningCandidates = candidates.filter(candidate =>
    candidate.jobId == JobId && candidate.status != "not_selected" && candidate.status != "rejected"
  );

  const sortCandidates = (candidates: any[], isFiltered: boolean) => {
    return candidates.sort((a, b) => {
      if (isFiltered) {
        if (a.score !== b.score) {
          return b.score - a.score;
        }
        const statusPriority: Record<string, number> = {
          final_screening: 3,
          initial_screening: 2,
          rejected_by_hr: 1
        };
        return (statusPriority[b.status as CandidateStatus] || 0) - (statusPriority[a.status as CandidateStatus] || 0);
      } else {
        // Default: Status priority first, then score
        const statusPriority: Record<string, number> = {
          final_screening: 3,
          initial_screening: 2,
          rejected_by_hr: 1
        };
        const statusDiff = (statusPriority[b.status as CandidateStatus] || 0) - (statusPriority[a.status as CandidateStatus] || 0);
        return statusDiff !== 0 ? statusDiff : b.score - a.score;
      }
    });
  };

  // Apply filter and sorting
  const filteredCandidates = selectedFilter
    ? sortCandidates([...finalScreeningCandidates], true).slice(0, selectedFilter)
    : sortCandidates([...finalScreeningCandidates], false);
  const selectedCandidate = filteredCandidates.find(c => c.candidate_id === openProfile);

  const handleReject = (candidateId: number, jobId: number) => {
    updateCandidateStatusLocally(candidateId, jobId, "rejected_by_hr");
    setOpenProfile(null);
  };

  const handleShortlist = (candidateId: number, jobId: number) => {
    updateCandidateStatusLocally(candidateId, jobId, "final_screening");
    setOpenProfile(null);
  };

  const handleFilterSelect = (count: number) => {
    setSelectedFilter(count);
    toast.success(`Showing top ${count} candidates`);
  };

  const clearFilter = () => {
    setSelectedFilter(null);
    toast.success("Filter cleared - showing all candidates");
  };

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

  useEffect(() => {
    fetchCandidates();
  }, [fetchCandidates]);
  return (
    <div className="p-4 pb-1 w-screen flex flex-col gap-4">
      <div className="flex flex-row justify-between w-full gap-4">
        {/* Filter Dropdown */}
        <div className="flex md:flex-row flex-col  md:items-center items-start gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button className="bg-blue text-white font-inter-regular hover:scale-105 gap-2">
                <Filter className="w-4 h-4" />
                Filter
                {selectedFilter && (
                  <Badge className="bg-white text-blue font-inter-regular ml-1">
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
            onClick={() => generateExcelReport(parseInt(JobId ?? "0"))}
            disabled={loading}
            className="bg-green text-white font-inter-regular hover:scale-105 transition-all duration-200"
          >
            {loading ? (
              <>
                generating
              </>
            ) : "Download Excel"}

          </Button>
        </div>
        <Button
          className={`bg-gradient-to-bl from-green to-blue text-white font-inter-regular hover:scale-105 transition-all duration-200 ${!hasUnsavedChanges ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          disabled={!hasUnsavedChanges}
          onClick={handleSaveChanges}
        >
          Save Changes {hasUnsavedChanges && changedCandidates ? `(${changedCandidates.size})` : ''}
        </Button>
      </div>
      <Card className="w-full shadow">
        <CardHeader className="flex flex-row items-center gap-2 pb">
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
              {filteredCandidates.length > 0 ? (
                filteredCandidates.slice(0, 5).map((candidate, idx) => (
                  <TableRow key={candidate.candidate_id ?? idx}>
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
        <div className="flex flex-row justify-center w-full pb-4">
          {/* Score Cards */}
          <div
            className={`flex flex-col gap-2 items-start justify-start transition-all duration-300 ${openProfile !== null ? "md:w-1/2 w-full h-[90vh] overflow-y-scroll p-2 pb-4" : "w-full"
              }`}
          >
            {loading ? (
              <Loading />
            ) : filteredCandidates.length > 0 ? (
              // Show filtered candidates when data is available
              filteredCandidates.map((candidate) => {
                console.log("Debug candidate_id:", candidate.candidate_id); // <-- Debug here
                return (
                  <CandidatesScoreCard
                    key={`${candidate.candidate_id}-${candidate.status}`}
                    name={candidate.name}
                    status={candidate.status}
                    score={candidate.score}
                    recommendation={candidate.recommendation}
                    onViewProfile={() => setOpenProfile(candidate.candidate_id)}
                  />
                );
              })
            ) : (
              // Show NoData component when no candidates found
              <NoData title="No candidates assigned to this job." />
            )}
          </div>

          {/* Side Dialog */}
          {openProfile !== null && selectedCandidate && (
            <>
              {/* Desktop: Side Card */}
              <div className="hidden relative py-2 pb-4 sm:flex h-[90vh] overflow-y-scroll w-[60%] items-start justify-center">
                <CandidateProfileDialog
                  open={openProfile !== null}
                  onOpenChange={(open) => !open && setOpenProfile(null)}
                  id={selectedCandidate.candidate_id}
                  candidate={selectedCandidate}
                  onReject={() => handleReject(selectedCandidate?.candidate_id, selectedCandidate?.jobId)}
                  Shortlist={() => handleShortlist(selectedCandidate?.candidate_id, selectedCandidate?.jobId)}
                />
              </div>
              {/* Mobile: Overlay Dialog */}
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 sm:hidden">
                <div className="w-[95vw] max-h-[95vh] overflow-y-auto">
                  <CandidateProfileDialog
                    open={openProfile !== null}
                    onOpenChange={(open) => !open && setOpenProfile(null)}
                    id={selectedCandidate.candidate_id}
                    candidate={selectedCandidate}
                    onReject={() => handleReject(selectedCandidate?.candidate_id, selectedCandidate?.jobId)}
                    Shortlist={() => handleShortlist(selectedCandidate?.candidate_id, selectedCandidate?.jobId)}
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