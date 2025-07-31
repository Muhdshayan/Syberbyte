import type { User } from "@/dashboard/adminDashboard/admin-store";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableCell,
  TableHead,
} from "@/components/ui/table";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { MoreVertical, Edit, Key, Trash2 } from "lucide-react";
import {useAuthStore} from "@/Login/useAuthStore";

interface WebTableProps {
  users: User[];
  onEditUser?: (user: User) => void;
  onResetUser?: (user: User) => void;
  onDeleteUser?: (user: User) => void;
}

export default function WebTable({ users, onEditUser, onResetUser, onDeleteUser }: WebTableProps) {
  const permission = useAuthStore((state) => state.authUser?.permission);
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>User</TableHead>
          <TableHead>Role</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Last Active</TableHead>
          {permission == 10 && (<TableHead className="text-left">Actions</TableHead>)}
          
        </TableRow>
      </TableHeader>
      <TableBody>
        {users.map((user, index) => (
          <TableRow key={user.id ?? index}>
            <TableCell>
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
            </TableCell>
            <TableCell align="left">
              <Badge variant="outline">{user.role}</Badge>
            </TableCell>
            <TableCell align="left">
              <Badge
                className={
                  user.status === "Active"
                    ? "bg-green-100 text-green-700"
                    : "bg-red-100 text-red-700"
                }
              >
                {user.status}
              </Badge>
            </TableCell>
            <TableCell align="left">{user.lastActive}</TableCell>
            {permission == 10 && (
              <>
            <TableCell className="text-right">
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
            </TableCell>
              </>
            )}
            
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}