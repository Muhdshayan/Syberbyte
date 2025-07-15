import { useEffect, useState } from "react";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";
import MobileTable from "@/dashboard-components/mobile-table";
import EditUserDialog from "@/dashboard-components/edit-user";
import DeleteUserDialog from "./delete-user";
import ResetPasswordDialog from "./reset-password";
import { useAdminStore } from "@/dashboard/adminDashboard/admin-store";
import type { User } from "@/dashboard/adminDashboard/admin-store"; // <-- add this
import WebTable from "./webTable";

export default function UserTable() {
  const [editUser, setEditUser] = useState<User | null>(null);
  const [deleteUser, setDeleteUser] = useState<User | null>(null);
  const [resetUser, setResetUser] = useState<User | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const usersPerPage = 3;
  

  // Fetch users from store
  const users = useAdminStore((state) => state.users);

  const fetchUsers = useAdminStore((state) => state.fetchUsers);
  const editUserInStore = useAdminStore((state) => state.editUser);
  const deleteUserFromStore = useAdminStore((state) => state.deleteUser);
  const resetUserPassword = useAdminStore((state) => state.resetPassword);


  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const indexOfLastUser = currentPage * usersPerPage;
  const indexOfFirstUser = indexOfLastUser - usersPerPage;
  const currentUsers = Array.isArray(users) ? users.slice(indexOfFirstUser, indexOfLastUser) : [];
  const totalPages = Math.ceil(users.length / usersPerPage);

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

        {/* Web Table */}
        <div className="hidden md:block w-full">
          <WebTable
            users={currentUsers}
            onEditUser={setEditUser}
            onResetUser={setResetUser}
            onDeleteUser={setDeleteUser}
          />
        </div>

        {/* Mobile Table */}
        <div className="block md:hidden w-full">
          <MobileTable
            users={currentUsers} // Pass current users to MobileTable
            onEditUser={(u) => setEditUser(u)}
            onResetUser={(u) => setResetUser(u)}
            onDeleteUser={(u) => setDeleteUser(u)}
          />
        </div>
        <div className="flex justify-between items-center mt-5">
          <p className="text-sm text-muted-foreground">
            Showing {indexOfFirstUser + 1}-{Math.min(indexOfLastUser, users.length)} of {users.length} users
          </p>
          <div className="flex gap-2">
            <Button
              className="!bg-blue"
              onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft />
            </Button>
            <Button
              className="!bg-blue"
              onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
            >
              <ChevronRight />
            </Button>
          </div>
        </div>
          {editUser && (
          <EditUserDialog
            user={editUser}
            open={!!editUser}
            onOpenChange={(open: boolean) => !open && setEditUser(null)}
            onSave={(updatedUser: User) => {
              editUserInStore(updatedUser);
              setEditUser(null);
           }}
          />
        )}
         {deleteUser && (
          <DeleteUserDialog
            open={!!deleteUser}
            onOpenChange={(open: boolean) => !open && setDeleteUser(null)}
            onDelete={() => {
              deleteUserFromStore(deleteUser.id); // <-- pass id to store
              setDeleteUser(null);
            }}
          />
        )}
        {resetUser && (
          <ResetPasswordDialog
            open={!!resetUser}
            onOpenChange={(open: boolean) => !open && setResetUser(null)}
            email={resetUser.email}
            onReset={(password: string) => {
              resetUserPassword(resetUser.id, password); // <-- call store function
              setResetUser(null);
            }}
          />
        )}
      </Card>
    </div>
  );
}