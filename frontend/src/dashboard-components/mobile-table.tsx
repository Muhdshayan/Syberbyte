import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { MoreVertical } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { Edit, Trash2, Key } from "lucide-react";
import type {User} from "@/dashboard/adminDashboard/admin-store"


interface MobileTableProps {
  users: User[];
  onEditUser?: (user: User) => void;
  onResetUser?: (user: User) => void;
  onDeleteUser?: (user: User) => void;
}

export default function MobileTable({ users, onEditUser, onResetUser, onDeleteUser }: MobileTableProps) {
  return (
       <>
      {users.map(user => (
        <Card key={user.id} className="w-full p-5 font-inter-regular mb-3">
          <div className="flex flex-row justify-between items-center">
            <div className="flex items-center gap-3">
              <Avatar className="h-8 w-8">
                <AvatarFallback>
                  {user.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")
                    .toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div>
                <p className="text-sm text-left font-medium">{user.name}</p>
                <p className="text-xs text-left text-muted-foreground">{user.email}</p>
              </div>
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <MoreVertical className="w-5 h-5 cursor-pointer" />
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  className="justify-between"
                  onClick={() => onEditUser && onEditUser(user)}
                >
                  Edit User <Edit className="w-6 h-6 text-green" />
                </DropdownMenuItem>
                <DropdownMenuItem
                  className="justify-between"
                  onClick={() => onResetUser && onResetUser(user)}
                >
                  Reset Password <Key className="w-6 h-6 text-green" />
                </DropdownMenuItem>
                <DropdownMenuItem
                  className="justify-between text-red-600"
                  onClick={() => onDeleteUser && onDeleteUser(user)}
                >
                  Delete User <Trash2 className="w-6 h-6 text-green" />
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
          <div className="flex flex-col justify-center items-center w-full">
            <div className="flex flex-row justify-between w-full">
              <p>Role</p>
              <Badge variant="outline">{user.role}</Badge>
            </div>
            <div className="flex flex-row justify-between w-full mt-2">
              <p>Status</p>
              <Badge
                className={
                  user.status === "Active"
                    ? "bg-green-100 text-green-700"
                    : "bg-red-100 text-red-700"
                }
              >
                {user.status}
              </Badge>
            </div>
            <div className="flex flex-row justify-between w-full">
              <p>Last Active</p>
              <span>{user.lastActive}</span>
            </div>
          </div>
        </Card>
      ))}
    </>
  );
}