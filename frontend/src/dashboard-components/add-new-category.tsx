import { CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Plus } from "lucide-react";
import { useState } from "react";
import { useAdminStore } from "@/dashboard/adminDashboard/admin-store";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";
import { getCategoryStats } from "@/dashboard/adminDashboard/admin-store";

export default function AddCategory() {
  const [description, setDescription] = useState("");
  const [educationLevel, setEducationLevel] = useState("");
  const [experienceLevel, setExperienceLevel] = useState("");
  const [industry, setIndustry] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [jobType, setJobType] = useState("");
  const [location, setLocation] = useState("");
  const [role, setRole] = useState("");
  const [salary, setSalary] = useState("");
  const [skills, setSkills] = useState("");
  const addJobCategory = useAdminStore((state) => state.addCategory);
  const [loading, setLoading] = useState(false);

  const jobCategories = useAdminStore(state => state.jobCategories); 
  const { total, active } = getCategoryStats(jobCategories);

  const handleAddCategory = async () => {
    if (
      !description ||
      !educationLevel ||
      !experienceLevel ||
      !industry ||
      !jobType ||
      !location ||
      !role ||
      !salary ||
      !skills
    )
      return;
    setLoading(true);
    const currentDate = new Date().toISOString().split("T")[0]; // Format as YYYY-MM-DD
    await addJobCategory({
      job_id: 1, // Set as undefined to satisfy interface while letting backend handle it
      posted_by: 4,
      assigned_to: 5,
      date_posted: currentDate,
      description,
      education_level: educationLevel,
      experience_level: experienceLevel,
      industry,
      is_active: isActive,
      job_type: jobType,
      location,
      role,
      salary,
      salary_currency: "USD",
      salary_period: "year",
      skills: skills.split(",").map((s) => s.trim()).filter(Boolean).join(","),
    });
    setDescription("");
    setEducationLevel("");
    setExperienceLevel("");
    setIndustry("");
    setIsActive(true);
    setJobType("");
    setLocation("");
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
        {/* Description */}
        <div>
          <Label htmlFor="description">Description</Label>
          <Input
            id="description"
            placeholder="Enter Job Description"
            className="w-full mt-2 bg-white"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        {/* Education Level */}
        <div>
          <Label htmlFor="educationLevel">Education Level</Label>
          <Input
            id="educationLevel"
            placeholder="Enter Education Level"
            className="w-full mt-2 bg-white"
            value={educationLevel}
            onChange={(e) => setEducationLevel(e.target.value)}
          />
        </div>
        {/* Experience Level */}
        <div>
          <Label htmlFor="experienceLevel">Experience Level</Label>
          <Input
            id="experienceLevel"
            placeholder="Enter Experience Level"
            className="w-full mt-2 bg-white"
            value={experienceLevel}
            onChange={(e) => setExperienceLevel(e.target.value)}
          />
        </div>
        {/* Industry */}
        <div>
          <Label htmlFor="industry">Industry</Label>
          <Input
            id="industry"
            placeholder="Enter Industry"
            className="w-full mt-2 bg-white"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
          />
        </div>
        {/* Job Type */}
        <div>
          <Label htmlFor="jobType">Job Type</Label>
          <Select
            value={jobType}
            onValueChange={setJobType}
          >
            <SelectTrigger id="jobType" className="w-full mt-2 !bg-white !border-gray-200 !text-primary !text-sm">
              <SelectValue placeholder="Select Job Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Full-time">Full Time</SelectItem>
              <SelectItem value="Part-time">Part Time</SelectItem>
              <SelectItem value="Contract">Contract</SelectItem>
            </SelectContent>
          </Select>
        </div>
        {/* Location */}
        <div>
          <Label htmlFor="location">Location</Label>
          <Input
            id="location"
            placeholder="Enter Location"
            className="w-full mt-2 bg-white"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
        </div>
        {/* Role */}
        <div>
          <Label htmlFor="role">Role</Label>
          <Input
            id="role"
            placeholder="Enter Role"
            className="w-full mt-2 bg-white"
            value={role}
            onChange={(e) => setRole(e.target.value)}
          />
        </div>
        {/* Salary */}
        <div>
          <Label htmlFor="salary">Salary</Label>
          <Input
            id="salary"
            placeholder="Enter Salary Range"
            className="w-full mt-2 bg-white"
            value={salary}
            onChange={(e) => setSalary(e.target.value)}
          />
        </div>
        {/* Required Skills */}
        <div>
          <Label htmlFor="skills">Required Skills</Label>
          <Input
            id="skills"
            placeholder="Comma separated (e.g., Python, SQL, Excel)"
            className="w-full mt-2 bg-white"
            value={skills}
            onChange={(e) => setSkills(e.target.value)}
          />
        </div>

      </CardContent>
      <CardFooter className="mt-6 flex flex-col gap-2">
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
            <p>{total}</p>
          </div>
          <div className="mt-1 w-full flex justify-between font-inter-regular text-sm">
            <p>Active Jobs</p>
            <p>{active}</p>
          </div>
        </div>
      </CardFooter>
    </div>
  );
}