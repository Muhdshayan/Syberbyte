import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Search, Filter } from "lucide-react";
import { useState } from "react";

export default function SearchJobCategory() {
  const [industry, setIndustry] = useState("");
  const [role, setRole] = useState("");

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
          />
        </div>
        {/* Industry Select */}
        <div className="flex md:w-[70%] w-full md:gap-2 gap-1">
          <Select value={industry} onValueChange={setIndustry}>
            <SelectTrigger className=" md:min-w-[140px] w-full !border-gray-200 !bg-white">
              <SelectValue placeholder="Select Industry" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="IT">IT</SelectItem>
              <SelectItem value="Finance">Finance</SelectItem>
              <SelectItem value="Healthcare">Healthcare</SelectItem>
            </SelectContent>
          </Select>
        </div>
        {/* Role Select */}
        <div className="flex w-full gap-2">
        <Select value={role} onValueChange={setRole}>
          <SelectTrigger className=" md:min-w-[140px] w-full !bg-white !border-gray-200">
            <SelectValue placeholder="Select Role" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Admin">Admin</SelectItem>
            <SelectItem value="Recruiter">Recruiter</SelectItem>
            <SelectItem value="HR Manager">HR Manager</SelectItem>
          </SelectContent>
        </Select>
        {/* Filter Button */}
        <Button className="!bg-green flex items-center gap-2">
          <Filter className="h-4 w-4" />
          Filter
        </Button>
        </div>
      </Card>
    </div>
  );
}