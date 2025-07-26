import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useHrStore } from "../dashboard/HrDashboard/hr-store"; // Updated to use hr-store.tsx

interface DeleteJobCategoryDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  jobId: number;
  onDelete: () => void;
}

export default function DeleteJobCategoryDialog({
  open,
  onOpenChange,
  jobId,
  onDelete,
}: DeleteJobCategoryDialogProps) {
  const { deleteJob } = useHrStore(); // Use deleteJob from hr-store

  const handleDelete = async () => {
    try {
      await deleteJob(jobId); // Call deleteJob with jobId
      onDelete(); // Close the dialog on successful deletion
    } catch (err) {
      // Error handling is managed by the store's toast notifications
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="md:max-w-md md:w-full w-[80%] font-inter-regular">
        <DialogHeader className="w-[80%]">
          <DialogTitle className="font-poppins-semibold">Are you sure you want to delete this job?</DialogTitle>
          <DialogDescription>
            This action cannot be undone. This will permanently delete the job and remove its data from servers.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="flex justify-end gap-2">
          <Button
            className="!bg-gray-300 !text-black !text-sm hover:!bg-gray-400"
            type="button"
            onClick={() => onOpenChange(false)}
          >
            Cancel
          </Button>
          <Button className="!bg-red-500 !text-sm" type="button" onClick={handleDelete}>
            Delete
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}