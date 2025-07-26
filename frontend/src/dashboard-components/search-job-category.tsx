import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Search } from "lucide-react";
import { useState } from "react";
import { useAdminStore } from "@/dashboard/adminDashboard/admin-store";
import { useMemo } from "react";
import { X } from "lucide-react";
import JobCategoryTable from "./job-category-table";



export default function SearchJobCategory() {
  const [filters, setFilters] = useState({
    search: "",
    industry: "",
    role: "",
  });
  const searchCategory = useAdminStore((state) => state.searchCategory);
  const jobCategories = useAdminStore((state) => state.jobCategories);
 
   const uniqueIndustries = useMemo(
    () => Array.from(new Set(jobCategories.map(cat => cat.industry))),
    [jobCategories]
  );
  const uniqueRoles = useMemo(
    () => Array.from(new Set(jobCategories.map(cat => cat.role))),
    [jobCategories]
  );

   const filteredCategories = useMemo(() => {
    const query = [filters.search, filters.industry, filters.role].filter(Boolean).join(" ");
    return query.trim() ? searchCategory(query) : jobCategories;
  }, [filters, jobCategories, searchCategory]);

  const isFilterApplied = !!(filters.search || filters.industry || filters.role);


 return (
    <div className="flex flex-col items-start mt-5 justify-start w-full !font-inter-regular">
      <Card className="w-[99%] p-3 flex items-center gap-3 md:flex-row flex-col">
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
              }}
          />
        </div>
        {/* Industry Select */}
        <div className="flex md:w-[70%] w-full md:gap-2 gap-1">
          <Select 
          value={filters.industry} 
          onValueChange={val => 
            {setFilters(f => ({ ...f, industry: val }))
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
          <Button
            className="!bg-green"
            onClick={() => setFilters({ search: "", industry: "", role: "" })}
            title="Clear filters"
          >
            <X />
          </Button>
        </div>
      </Card>
      <JobCategoryTable categories={isFilterApplied ? filteredCategories : jobCategories} />

    </div>
  );
}
