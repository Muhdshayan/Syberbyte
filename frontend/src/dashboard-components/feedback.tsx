import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { MessageSquare } from "lucide-react";
import { CircularProgress } from "@mui/material";
import { toast } from "sonner";
import { useHrStore } from "@/dashboard/HrDashboard/hr-store";

interface FeedbackDialogProps {
  candidateId: number;
  jobId: number;
  candidateName?: string;
  currentScore?: number;
  children?: React.ReactNode;
}

export default function FeedbackDialog({ 
  candidateId, 
  jobId, 
  candidateName,
  currentScore,
  children 
}: FeedbackDialogProps) {
  const [open, setOpen] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [correctScore, setCorrectScore] = useState(currentScore?.toString() || "");
  const [loading, setLoading] = useState(false); // Local loading state
  
  const submitFeedback = useHrStore((state) => state.submitFeedback);

  const handleSubmit = async () => {
    // Validation
    if (!feedback.trim()) {
      toast.error("Please provide feedback");
      return;
    }

    if (!correctScore || isNaN(Number(correctScore)) || Number(correctScore) < 0 || Number(correctScore) > 100) {
      toast.error("Please provide a valid score between 0-100");
      return;
    }

    setLoading(true); // Set local loading to true
    
    try {
      await submitFeedback({
        candidateId,
        jobId,
        feedback: feedback.trim(),
        correctScore: Number(correctScore),
        timestamp: new Date().toISOString(),
      });

      // Reset form and close dialog on success
      setOpen(false);
      setFeedback("");
      setCorrectScore(currentScore?.toString() || "");
      toast.success("Feedback submitted successfully!");
      
    } catch (error) {
      console.error("Error submitting feedback:", error);
      toast.error("Failed to submit feedback");
    } finally {
      setLoading(false); // Always reset loading state
    }
  };

  const handleCancel = () => {
    setOpen(false);
    setFeedback("");
    setCorrectScore(currentScore?.toString() || "");
    setLoading(false); // Reset loading on cancel
  };

  // Reset form when dialog closes
  const handleOpenChange = (isOpen: boolean) => {
    setOpen(isOpen);
    if (!isOpen) {
      setFeedback("");
      setCorrectScore(currentScore?.toString() || "");
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        {children || (
          <Button variant="ghost" size="sm" className="text-gray-400 hover:text-gray-600">
            <MessageSquare className="w-4 h-4 mr-2" />
            Give Feedback
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            Provide Feedback
          </DialogTitle>
          <DialogDescription>
            Help us improve our AI matching by providing feedback 
            {candidateName && ` for ${candidateName}`}
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          {/* Feedback Text */}
          <div className="space-y-2">
            <Label htmlFor="feedback">Feedback *</Label>
            <Textarea
              id="feedback"
              placeholder="Tell us what's wrong with this match or how we can improve..."
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              rows={4}
              className="resize-none"
              disabled={loading} // Disable when loading
            />
          </div>

          {/* Correct Score */}
          <div className="space-y-2">
            <Label htmlFor="correctScore">What should the correct score be? (0-100) *</Label>
            <Input
              id="correctScore"
              type="number"
              min="0"
              max="100"
              placeholder="Enter score (0-100)"
              value={correctScore}
              onChange={(e) => setCorrectScore(e.target.value)}
              disabled={loading} // Disable when loading
            />
            {currentScore && (
              <div className="text-xs text-gray-500">
                Current AI score: {currentScore}%
              </div>
            )}
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button 
            variant="outline" 
            onClick={handleCancel}
            disabled={loading} // Disable when loading
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit}
            disabled={loading || !feedback.trim() || !correctScore} // Better disabled state
            className="bg-blue-600 hover:bg-blue-700 flex items-center gap-2 min-w-[120px]"
          >
            {loading ? (
              <>
                <CircularProgress size={16} sx={{ color: 'white' }} />
                Submitting...
              </>
            ) : (
              "Send Feedback"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}