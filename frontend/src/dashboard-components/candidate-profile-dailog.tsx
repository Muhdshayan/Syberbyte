import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import type { Candidate } from "@/dashboard/RecruiterDashboard/recruiter-store"; // Adjust path as needed
import { useAuthStore } from "@/Login/useAuthStore";
import FeedbackDialog from "./feedback";
import { Document, Page, pdfjs } from 'react-pdf';
import { useState } from 'react';

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;


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
  const [numPages, setNumPages] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
    const goToPrevPage = () => {
    setCurrentPage(page => Math.max(1, page - 1));
  };

  const goToNextPage = () => {
    setCurrentPage(page => Math.min(numPages, page + 1));
  };
  const pdfUrl = "/resume.pdf";
  
  if (!open) return null;
  
  return (
    <Card className="w-full shadow-lg p-6 relative animate-in fade-in font-inter-regular">
      <div className="flex justify-between items-start">
        <div>
          <div className="text-2xl font-poppins-semibold">{candidate.name}</div>
        </div>
        <X className="w-5 h-5 cursor-pointer hover:text-gray-600" onClick={() => onOpenChange(false)}/>
      </div>
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <span className="font-inter-semibold">{candidate.role}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-inter-semibold">Match score</span>
          <span className="bg-green text-white rounded-full px-3 py-1 text-sm font-medium">
            {candidate.score}%
          </span>
        </div>
      </div>
      {/* Match Confidence Breakdown */}
      <div className="rounded-xl p-4  bg-gradient-to-br from-green to-blue">
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
      <div className="h-auto overflow-y-scroll flex flex-col">
          <Document
            file={pdfUrl}
            onLoadSuccess={({ numPages }) => {
              setNumPages(numPages);
              setCurrentPage(1); // Reset to first page when PDF loads
            }}
            loading={<div className="h-full w-full judtify-center items-center">Loading PDF...</div>}
            className="flex-1 flex justify-center"
          >
            <Page 
              pageNumber={currentPage} 
              scale={window.innerWidth > 600 ? 1.1 : 0.5}
              renderAnnotationLayer={false} 
              renderTextLayer={false}
              className="mx-auto"
            />
          </Document>
          
          {/* Page Navigation Controls */}
          {numPages > 1 && (
            <div className="flex justify-center items-center gap-4 py-4 bg-white border-t">
              <Button
                onClick={goToPrevPage}
                disabled={currentPage <= 1}
                variant="outline"
                size="sm"
              >
                Previous
              </Button>
              
              <span className="text-sm font-medium">
                Page {currentPage} of {numPages}
              </span>
              
              <Button
                onClick={goToNextPage}
                disabled={currentPage >= numPages}
                variant="outline"
                size="sm"
              >
                Next
              </Button>
            </div>
          )}
        </div>
      <div className="flex justify-between items-center gap-2 mt-6">
        <Button className="!bg-red-500 !text-sm" onClick={onReject}>
          Reject
        </Button>
        
        {permission === 3 && (
          <FeedbackDialog 
            candidateId={candidate.id}
            jobId={candidate.jobId}
            candidateName={candidate.name}
            currentScore={candidate.score}
          >
            <p className="text-sm text-gray-400 cursor-pointer hover:text-gray-600 hover:underline">
              Not satisfied? Give feedback
            </p>
          </FeedbackDialog>
        )}
        
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