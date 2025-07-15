import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useAdminStore } from "@/dashboard/adminDashboard/admin-store";
import {
  Table,
  TableBody,
  TableRow,
  TableCell,
} from "@/components/ui/table";
import { X } from "lucide-react";
import MobileTable from "@/dashboard-components/mobile-table";
import WebTable from "./webTable";

export default function SearchUser() {
  const [query, setQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState<string | null>(null);
  const [inputActive, setInputActive] = useState(false);
  const searchUser = useAdminStore((state) => state.searchUser);
  const users = searchUser(query);

  // Optional: filter by role if a role button is clicked
  const filteredUsers = roleFilter
    ? users.filter((u) => u.role.toLowerCase() === roleFilter.toLowerCase())
    : users;

  return (
    <div className="flex flex-col items-start mt-5 justify-start w-full !font-inter-regular">
      <Card className="w-[95%] p-3 flex md:flex-row flex-col justify-between">
        <div className="flex gap-2">
          <div className="relative z-1">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              <Search className="h-5 w-5" />
            </span>
            <Input
              placeholder="Search by name or email"
              className="pl-10"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onFocus={() => setInputActive(true)}
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
        <div className="flex md:gap-2 gap-1">
          <Button
              className="!bg-blue !text-sm !font-inter-regular !px-2"
              onClick={() => {
                setRoleFilter("Admin");
                setInputActive(true); // keep card open
              }}
            >
              Admin
            </Button>
            <Button
              className="!bg-blue !text-sm !font-inter-regular !px-2"
              onClick={() => {
                setRoleFilter("Recruiter");
                setInputActive(true);
              }}
            >
              Recruiter
            </Button>
            <Button
              className="!bg-blue !text-sm !font-inter-regular !px-2"
              onClick={() => {
                setRoleFilter("HR Manager");
                setInputActive(true);
              }}
            >
              Hr Manager
            </Button>
            <Button className="!bg-green" onClick={() => { setInputActive(false); setRoleFilter(null); }}>
                <X />
            </Button>
        </div>
      </Card>
      {inputActive && (
        <>
          <Card className="p-4 w-[95%] hidden md:block mt-5 transition-all duration-300 ease-in-out opacity-100 translate-y-0 animate-fade-in">
            <Table>
              <TableBody>
                {query.trim() === "" && !roleFilter ?  (
                  <TableRow>
                    <TableCell colSpan={4} className="text-black text-sm">
                      Please enter a search query.
                    </TableCell>
                  </TableRow>
                ) : filteredUsers.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} className="text-black text-sm">
                      No users found.
                    </TableCell>
                  </TableRow>
                ) : (
                    <div className="hidden md:block w-[95%] mt-5">
                      <WebTable users={filteredUsers} />
                     </div>
                )}
              </TableBody>
            </Table>
          </Card>
          {/* Mobile List */}
            <div className="md:hidden block w-[95%] mt-5">
                <MobileTable users={filteredUsers} />
            </div>
        </>
      )}
    </div>
  );
}