import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface DeleteJobCategoryDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onDelete: () => void;
}

export default function DeleteJobCategoryDialog({
  open,
  onOpenChange,
  onDelete,
}: DeleteJobCategoryDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="md:max-w-md md:w-full w-[80%] font-inter-regular">
        <DialogHeader className="w-[80%]">
          <DialogTitle className="font-poppins-semibold">Are you sure you want to delete this job?</DialogTitle>
          <DialogDescription>
            This action cannot be undone. This will permanently delete job category and remove job data from servers.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="flex justify-end gap-2">
          <Button className="!bg-red-500 !text-sm" type="button" onClick={onDelete}>
            Delete
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}