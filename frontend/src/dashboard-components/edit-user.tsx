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
import type { User, UserStatus} from "@/dashboard/adminDashboard/admin-store";


interface EditUserDialogProps {
  user: User;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (user: User) => void;
}

export default function EditUserDialog({ user, open, onOpenChange, onSave }: EditUserDialogProps) {
  const [form, setForm] = useState<User>(user);

    const handleRoleChange = (role: string) => {
      setForm({ ...form, role: role });
    };

    const handleStatusChange = (status: string) => {
      setForm({ ...form, status: status as UserStatus });
    };

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
            onSave(form);
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
              onValueChange={handleRoleChange}>
              <SelectTrigger className="w-full !bg-white !text-primary !border-gray-200 !outline-none">
                <SelectValue placeholder="Select role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Advanced Admin">Advanced Admin</SelectItem>
                <SelectItem value="Basic Admin">Basic Admin</SelectItem>
                <SelectItem value="Full Admin">Full Admin</SelectItem>
                <SelectItem value="HR Manager">HR Manager</SelectItem>
                <SelectItem value="Recruiter">Recruiter</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Status</label>
            <Select
              value={form.status}
              onValueChange={handleStatusChange}
            >
              <SelectTrigger className="w-full !border-gray-200 !bg-white !outline-none">
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