import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useAdminStore } from "@/dashboard/adminDashboard/admin-store";
import { X } from "lucide-react";
import MobileTable from "@/dashboard-components/mobile-table";
import UserTable from "@/dashboard-components/user-table"; // <-- import your user-table component

import { Select, SelectTrigger, SelectContent, SelectItem } from "@/components/ui/select";


export default function SearchUser() {
  const [query, setQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState<string | null>(null);
  const searchUser = useAdminStore((state) => state.searchUser);
  const allUsers = useAdminStore((state) => state.users);


  // Filtered users by search and role
  const filteredUsers = searchUser(query).filter(u =>
    roleFilter ? u.role.toLowerCase() === roleFilter.toLowerCase() : true
  );

  const isFilterApplied = !!query || !!roleFilter;
  const usersToShow = isFilterApplied ? filteredUsers : allUsers;


  return (
    <div className="flex flex-col md:items-start items-center mt-5  justify-start md:w-full w-screen !font-inter-regular">
      <Card className="md:w-[99%] w-[95%] p-3 flex md:flex-row flex-col justify-between">
        <div className="flex gap-2 flex-1 min-w-[200px]">
          <div className="relative z-1 flex-grow">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              <Search className="h-5 w-5" />
            </span>
            <Input
              placeholder="Search by name or email"
              className="pl-10 w-full"
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>
          <div>
            <Button
              className="!bg-primary"
              onClick={() => setQuery("")}
              title="Clear search"
            >
              <Search className="h-5 w-5" />
            </Button>
          </div>
        </div>
        <div className="flex flex-wrap md:gap-2 gap-1 md:w-auto w-full">
          <Select
            value={roleFilter || ""}
            onValueChange={(value) => {
              setRoleFilter(value);
            }}
          >
            <SelectTrigger
              className={`!bg-blue !text-white !text-sm !font-inter-regular chevron-white ${roleFilter?.includes("admin") ? "!bg-white !text-blue-700 border border-blue-200" : "!bg-blue !text-white"}`}
            >
              Admin
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Basic Admin">Basic Admin</SelectItem>
              <SelectItem value="Advanced Admin">Advanced Admin</SelectItem>
              <SelectItem value="Full Admin">Full Admin</SelectItem>
            </SelectContent>
          </Select>
          <Button
            className={`!text-sm !font-inter-regular !px-2 ${roleFilter === "Recruiter" ? "!bg-white !text-blue-700 border border-blue-200" : "!bg-blue !text-white"}`}
            onClick={() => {
              setRoleFilter("Recruiter");

            }}
          >
            Recruiter
          </Button>
          <Button
            className={`!text-sm !font-inter-regular !px-2 ${roleFilter === "HR Manager" ? "!bg-white !text-blue-700 border border-blue-200" : "!bg-blue !text-white"}`}
            onClick={() => {
              setRoleFilter("HR Manager");
            }}
          >
            Hr Manager
          </Button>
          <Button className="!bg-green" onClick={() => { setRoleFilter(null); }}>
            <X />
          </Button>
        </div>
      </Card>
      <>
        {/* Desktop Table */}
        <div className="hidden md:block w-[99%] mt-5">
          <UserTable users={usersToShow} />
          {usersToShow.length === 0 && (
            <div className="text-black text-sm mt-4">No users found.</div>
          )}
        </div>
        {/* Mobile List */}
        <div className="md:hidden block w-[95%] mt-5">
          <MobileTable users={usersToShow} />
          {usersToShow.length === 0 && (
            <div className="text-black text-sm mt-4">No users found.</div>
          )}
        </div>
      </>
    </div>
  );
}