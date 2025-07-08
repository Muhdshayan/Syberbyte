import {useState} from "react";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableHeader, TableRow, TableHead,TableBody, TableCell } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { MoreHorizontal, Edit, Trash2, Key, ChevronLeft, ChevronRight} from "lucide-react";
import { Avatar, AvatarFallback} from "@/components/ui/avatar";
import MobileTable from "@/dashboard-components/mobile-table"
import EditUserDialog from "@/dashboard-components/edit-user";
import DeleteUserDialog from "./delete-user";
import ResetPasswordDialog from "./reset-password";

type UserStatus = "Active" | "Suspended";
type UserRole = "Admin" | "HR Manager" | "Recruiter";

interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  status: UserStatus;
  lastActive: string;
}

const users: User[] = [
  {
    id: 1,
    name: "User 1",
    email: "user1@company.com",
    role: "Admin",
    status: "Active",
    lastActive: "2 hours ago",
  },
  {
    id: 2,
    name: "User 1",
    email: "user1@company.com",
    role: "HR Manager",
    status: "Active",
    lastActive: "1 day ago",
  },
  {
    id: 3,
    name: "User 1",
    email: "user1@company.com",
    role: "Recruiter",
    status: "Suspended",
    lastActive: "3 days ago",
  },
];

export default function UserTable() {
  const [editUser, setEditUser] = useState<User | null>(null);
  const [open, setOpen] = useState(false);
  const [resetUser, setResetUser] = useState<User | null>(null);
  return (
    <div className="w-full flex items-center mt-5 justify-start">
      <Card className="w-[95%] p-5 font-inter-regular">
        <CardHeader>
          <CardTitle className="text-2xl font-poppins-semibold text-left text-primary">
            User Management
          </CardTitle>
          <CardDescription className="text-left">
            Manage user accounts, roles and permissions
          </CardDescription>
        </CardHeader>

        {/* Desktop Table */}
        <div className="hidden md:table w-full">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Last Active</TableHead>
                <TableHead className="text-left">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user, index) => (
                <TableRow key={index}>
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
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <MoreHorizontal className="w-5 h-5 cursor-pointer" />
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          className="justify-between"
                          onClick={() => setEditUser(user)}
                        >
                          Edit User <Edit className="w-6 h-6 text-green" />
                        </DropdownMenuItem>
                        <DropdownMenuItem 
                        className="justify-between"
                        onClick={() => setResetUser(user)}>
                          Reset Password<Key className="w-6 h-6 text-green" />
                        </DropdownMenuItem>
                        <DropdownMenuItem 
                        className="justify-between text-red-600"
                        onClick={() => setOpen(true)}>
                          Delete User<Trash2 className="w-6 h-6 text-green" />
                        </DropdownMenuItem>
                        
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          
        </div>

        {/* Mobile Table */}
        <div className="block md:hidden w-full">
          {users.map((user) => (
            <div key={user.id} className="mb-4">
              <MobileTable {...user} />
            </div>
          ))}
        </div>
        <div className="flex justify-between items-center mt-5">
            <p className="text-sm text-muted-foreground">
              Showing 1-3 of {users.length} users
            </p>
            <div>
              <Button className="!bg-blue">
                <ChevronLeft />
              </Button>
              <Button className="ml-2 !bg-blue">
                <ChevronRight />
              </Button>
            </div>
          </div>
          {editUser && (
          <EditUserDialog
            user={editUser}
            open={!!editUser}
            onOpenChange={(open: boolean) => !open && setEditUser(null)}
          />
        )}
        {open && (
          <DeleteUserDialog
            open={open}
            onOpenChange={(open: boolean) => setOpen(open)}
            onDelete={() => {
              // Your delete logic here
              setOpen(false);
            }}
          />
        )}
        {resetUser && (
          <ResetPasswordDialog
            open={!!resetUser}
            onOpenChange={(open: boolean) => !open && setResetUser(null)}
            email={resetUser.email}
            onReset={(password: string) => {
              // Your reset password logic here
              setResetUser(null);
            }}
          />
        )}
      </Card>
    </div>
  );
}