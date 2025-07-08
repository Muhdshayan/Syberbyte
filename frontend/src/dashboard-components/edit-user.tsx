import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { useState } from "react";

interface EditUserDialogProps {
  user: { name: string; email: string; role: string; status: string };
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function EditUserDialog({ user, open, onOpenChange }: EditUserDialogProps) {
  const [form, setForm] = useState(user);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-xs w-full !font-inter-regular">
        <DialogHeader>
          <DialogTitle className="font-poppins-semibold text-xl">Edit User</DialogTitle>
          <DialogDescription>
            Make changes to system users here. Click save when you're done.
          </DialogDescription>
        </DialogHeader>
        <form
          onSubmit={e => {
            e.preventDefault();
            // handle save here
          }}
          className="space-y-3"
        >
          <div>
            <label className="block text-sm font-medium mb-1">Full Name</label>
            <Input
              value={form.name}
              onChange={e => setForm({ ...form, name: e.target.value })}
              placeholder="Full Name"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <Input
              type="email"
              value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })}
              placeholder="Email"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Role</label>
            <Select
              value={form.role}
              onValueChange={role => setForm({ ...form, role })}
              
            >
              <SelectTrigger className="w-full !bg-white !outline-none">
                <SelectValue placeholder="Select role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Admin">Admin</SelectItem>
                <SelectItem value="HR Manager">HR Manager</SelectItem>
                <SelectItem value="Recruiter">Recruiter</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Status</label>
            <Select
              value={form.status}
              onValueChange={status => setForm({ ...form, status })}
            >
              <SelectTrigger className="w-full !bg-white !outline-none">
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Active">Active</SelectItem>
                <SelectItem value="Suspended">Suspended</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button type="submit" className="!bg-green !text-sm !text-inter-regular">
              Save changes
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}