import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Search, Filter } from "lucide-react";
import { useState } from "react";
import { useAdminStore } from "@/dashboard/adminDashboard/admin-store";
import type { JobCategory } from "@/dashboard/adminDashboard/admin-store"; // Import JobCategory type
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { MoreVertical, Edit, Trash2, X } from "lucide-react";
import JobCategoryMobTable from "./job-category-mob-table";
import { useMemo } from "react";


export default function SearchJobCategory() {
  const [filters, setFilters] = useState({
    search: "",
    industry: "",
    role: "",
  });
  const searchCategory = useAdminStore((state) => state.searchCategory);
  const [results, setResults] = useState<JobCategory[]>([]);
  const jobCategories = useAdminStore((state) => state.jobCategories);

   const uniqueIndustries = useMemo(
    () => Array.from(new Set(jobCategories.map(cat => cat.industry))),
    [jobCategories]
  );
  const uniqueRoles = useMemo(
    () => Array.from(new Set(jobCategories.map(cat => cat.role))),
    [jobCategories]
  );

   const handleFilter = () => {
    // Combine all filter values into a single query string
    const query = [filters.search, filters.industry, filters.role].filter(Boolean).join(" ");
    const filtered = searchCategory(query);
    setResults(filtered);
  };

 return (
    <div className="flex flex-col items-start mt-5 justify-start w-full !font-inter-regular">
      <Card className="w-[95%] p-3 flex items-center gap-3 md:flex-row flex-col">
        {/* Search Input */}
        <div className="relative w-full ">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            <Search className="h-5 w-5" />
          </span>
          <Input
            placeholder="Search Job Category"
            className="pl-10"
            value={filters.search}
            onChange={e => setFilters(f => ({ ...f, search: e.target.value }))}
          />
        </div>
        {/* Industry Select */}
        <div className="flex md:w-[70%] w-full md:gap-2 gap-1">
          <Select value={filters.industry} onValueChange={val => setFilters(f => ({ ...f, industry: val }))}>
            <SelectTrigger className=" md:min-w-[140px] w-full !border-gray-200 !bg-white">
              <SelectValue placeholder="Select Industry" />
            </SelectTrigger>
            <SelectContent>
              {uniqueIndustries.map(ind => (
                <SelectItem key={ind} value={ind}>{ind}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        {/* Role Select */}
        <div className="flex w-full gap-2">
           <Select value={filters.role} onValueChange={val => setFilters(f => ({ ...f, role: val }))}>
            <SelectTrigger className=" md:min-w-[140px] w-full !bg-white !border-gray-200">
              <SelectValue placeholder="Select Role" />
            </SelectTrigger>
            <SelectContent>
              {uniqueRoles.map(role => (
                <SelectItem key={role} value={role}>{role}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          {/* Filter Button */}
          <Button className="!bg-green flex items-center gap-2" onClick={handleFilter}>
            <Filter className="h-4 w-4" />
          </Button>
          <Button
            className="!bg-green"
            onClick={() => {
              setFilters({ search: "", industry: "", role: "" });
              setResults([]);
            }}
          >
            <X />
          </Button>
        </div>
      </Card>
      {/* Results Preview */}
      {results.length > 0 && (
        <div className="w-[95%] mt-4">
          <Card className="p-4 hidden md:block mt-5 transition-all duration-300 ease-in-out opacity-100 translate-y-0 animate-fade-in">
            {/* Desktop Table */}
            <div className="hidden md:block">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Industry</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Experience Level</TableHead>
                    <TableHead>Required Skills</TableHead>
                    <TableHead>Salary Range</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {results.map((cat, idx) => (
                    <TableRow key={idx}>
                      <TableCell align="left">{cat.industry}</TableCell>
                      <TableCell align="left">{cat.role}</TableCell>
                      <TableCell align="left">{cat.experience}</TableCell>
                      <TableCell align="left">
                        <div className="flex flex-wrap w-[200px] gap-1">
                          {cat.skills.map((skill, i) => (
                            <Badge key={i} className="bg-green text-white">{skill}</Badge>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell align="left">{cat.salary}</TableCell>
                      <TableCell align="center">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <MoreVertical className="w-5 h-5" />
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem
                              className="justify-between"
                              onClick={() => {/* implement edit logic here */}}
                            >
                              Edit Job <Edit className="w-5 h-5 text-green-600" />
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              className="justify-between text-red-600"
                              onClick={() => {/* implement delete logic here */}}
                            >
                              Delete Job <Trash2 className="w-5 h-5 text-green-600" />
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
            
          </Card>
          {/* Mobile Cards */}
            <div className="md:hidden block w-[95%] mt-5">
                  <JobCategoryMobTable
                    jobs={results} />
            </div>
        </div>
      )}
    </div>
  );
}
