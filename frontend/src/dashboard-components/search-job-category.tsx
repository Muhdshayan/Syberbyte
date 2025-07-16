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
  const [inputActive, setInputActive] = useState(false); // <-- add this
 
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
            onChange={e => {
              const value = e.target.value;
              setFilters(f => ({ ...f, search: value }));
              setInputActive(true);
              // Real-time filter
              const query = [value, filters.industry, filters.role].filter(Boolean).join(" ");
              setResults(searchCategory(query));
            }}
            onFocus={() => setInputActive(true)} // activate card on focus
          />
        </div>
        {/* Industry Select */}
        <div className="flex md:w-[70%] w-full md:gap-2 gap-1">
          <Select 
          value={filters.industry} 
          onValueChange={val => 
            {setFilters(f => ({ ...f, industry: val }))
            setInputActive(true);
            const query = [filters.search, val, filters.role].filter(Boolean).join(" ");
            setResults(searchCategory(query));
            }}>
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
           <Select
            value={filters.role}
            onValueChange={val => {
              setFilters(f => ({ ...f, role: val }));
              setInputActive(true); // activate card on select
              const query = [filters.search, filters.industry, val].filter(Boolean).join(" ");
              setResults(searchCategory(query));
            }}>
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
              setInputActive(false); 
              setResults([]);
            }}
          >
            <X />
          </Button>
        </div>
      </Card>
      {/* Results Preview */}
      {inputActive && (
  <>
    <Card className="p-4 w-[95%] hidden md:block mt-5 transition-all duration-300 ease-in-out opacity-100 translate-y-0 animate-fade-in">
      <Table>
        <TableBody>
          {filters.search.trim() === "" && !filters.industry && !filters.role ? (
            <TableRow>
              <TableCell colSpan={6} className="text-black text-sm">
                Please enter a search query or select a filter.
              </TableCell>
            </TableRow>
          ) : results.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="text-black text-sm">
                No job categories found.
              </TableCell>
            </TableRow>
          ) : (
            results.map((cat, idx) => (
              <TableRow key={idx}>
                <TableCell align="left">{cat.industry}</TableCell>
                <TableCell align="left">{cat.role}</TableCell>
                <TableCell align="left">{cat.experience}</TableCell>
                <TableCell align="left">
                  <div className="flex flex-wrap w-[200px] gap-1">
                    {(Array.isArray(cat.skills)
                      ? cat.skills
                      : String(cat.skills).split(",").map(s => s.trim())
                    ).map((skill, i) => (
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
            ))
          )}
        </TableBody>
      </Table>
    </Card>
    {/* Mobile Cards */}
    <div className="md:hidden block w-[95%] mt-5">
      {filters.search.trim() === "" && !filters.industry && !filters.role ? (
        <div className="text-center text-black text-sm bg-white rounded-lg py-8">
          Please enter a search query or select a filter.
        </div>
      ) : results.length === 0 ? (
        <div className="text-center text-black text-sm bg-white rounded-lg py-8">
          No job categories found.
        </div>
      ) : (
        <JobCategoryMobTable jobs={results} />
      )}
    </div>
  </>
)}
    </div>
  );
}
