import { CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { ChevronDown, Plus } from "lucide-react";
import { useState } from "react";
import { useAdminStore } from "@/dashboard/adminDashboard/admin-store";

export default function AddCategory() {
  const [industry, setIndustry] = useState("");
  const [experience, setExperience] = useState("");
  const [role, setRole] = useState("");
  const [salary, setSalary] = useState("");
  const [skills, setSkills] = useState("");
  const addJobCategory = useAdminStore((state) => state.addCategory);
  const [loading, setLoading] = useState(false);

  const handleAddCategory = async () => {
    if (!industry || !experience || !role || !salary || !skills) return;
    setLoading(true);
    await addJobCategory({
      industry,
      role,
      experience,
      skills: skills.split(",").map(s => s.trim()).filter(Boolean),
      salary,
    });
    setIndustry("");
    setExperience("");
    setRole("");
    setSalary("");
    setSkills("");
    setLoading(false);
  };

  return (
    <div className="md:w-[25%] w-full bg-cream shadow-none !font-inter-regular py-5">
      <CardHeader>
        <CardTitle className="text-2xl font-poppins-semibold text-left">Add New Category</CardTitle>
      </CardHeader>
      <CardContent className="!font-inter-regular mt-6 flex flex-col gap-4">
        {/* Industry */}
        <div>
          <Label htmlFor="industry">Industry</Label>
          <Input
            id="industry"
            placeholder="Enter Industry"
            className="w-full mt-2 bg-white"
            value={industry}
            onChange={e => setIndustry(e.target.value)}
          />
          <div className="text-secondary text-sm text-left mt-1">Select job technology</div>
        </div>
        {/* Experience Level */}
        <div>
          <Label htmlFor="experience">Experience Level</Label>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="outline"
                className="w-full !text-left !text-sm font-inter-regular !bg-white mt-2 !border-gray-200"
              >
                {experience ? experience : "Select Experience level"}
                <ChevronDown className="ml-auto h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-48 font-inter-regular" align="start">
              <DropdownMenuItem onClick={() => setExperience("Fresher")}>Fresher</DropdownMenuItem>
              <DropdownMenuItem onClick={() => setExperience("Mid Level")}>Mid Level</DropdownMenuItem>
              <DropdownMenuItem onClick={() => setExperience("Senior")}>Senior</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <div className="text-secondary text-sm text-left mt-1">Select job experience level</div>
        </div>
        {/* Role */}
        <div>
          <Label htmlFor="role">Role</Label>
          <Input
            id="role"
            placeholder="Enter Role"
            className="w-full mt-2 bg-white"
            value={role}
            onChange={e => setRole(e.target.value)}
          />
          <div className="text-secondary text-sm text-left mt-1">Select user role</div>
        </div>
        {/* Required Skills */}
        <div>
          <Label htmlFor="skills">Required Skills</Label>
          <Input
            id="skills"
            placeholder="Comma separated (e.g. Python, SQL, Excel)"
            className="w-full mt-2 bg-white"
            value={skills}
            onChange={e => setSkills(e.target.value)}
          />
          <div className="text-secondary text-sm text-left mt-1">Select Job Skills</div>
        </div>
        {/* Salary */}
        <div>
          <Label htmlFor="salary">Salary</Label>
          <Input
            id="salary"
            placeholder="Enter Salary Range"
            className="w-full mt-2 bg-white"
            value={salary}
            onChange={e => setSalary(e.target.value)}
          />
          <div className="text-secondary text-sm text-left mt-1">Select Salary Range</div>
        </div>
      </CardContent>
      <CardFooter className="mt-6 flex flex-col gap-5">
        <Button
          className="w-full !bg-blue"
          onClick={handleAddCategory}
          disabled={loading}
        >
          <Plus className="w-4 h-4" /> {loading ? "Creating..." : "Create Job Category"}
        </Button>
        <div className="font-inter-medium bg-green rounded-lg w-full text-white text-left p-5">
          Quick Stats
          <div className="mt-1 w-full flex justify-between font-inter-regular text-sm">
            <p>Total Job Category</p>
            <p>24</p>
          </div>
          <div className="mt-1 w-full flex justify-between font-inter-regular text-sm">
            <p>Active Jobs</p>
            <p>22</p>
          </div>
        </div>
      </CardFooter>
    </div>
  );
}