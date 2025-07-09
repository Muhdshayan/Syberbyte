import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MoreVertical, ChevronLeft, ChevronRight } from "lucide-react";

const jobCategories = [
  {
    industry: "Technology",
    role: "Software Engineering",
    experience: "Mid level",
    skills: ["Python", "JavaScript", "Node", "Git", "React", "SQL", "HTML", "CSS"],
    salary: "$80k-$100k",
  },
  {
    industry: "Healthcare",
    role: "Nurse",
    experience: "senior level",
    skills: ["Clinical", "Communication"],
    salary: "$80k-$100k",
  },
  {
    industry: "Finance",
    role: "Financial Analyst",
    experience: "Mid level",
    skills: ["Power BI", "Tableau", "Excel"],
    salary: "$80k-$100k",
  },
];

export default function JobCategoryTable() {
  return (
    <Card className="w-[95%] !font-inter-regular mt-5">
      <CardHeader>
        <CardTitle className="text-2xl font-poppins-semibold text-left">Job Category Management</CardTitle>
        <CardDescription className="text-left">Manage Job Categories</CardDescription>
      </CardHeader>
      <CardContent>
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
            {jobCategories.map((cat, idx) => (
              <TableRow key={idx}>
                <TableCell align="left">{cat.industry}</TableCell>
                <TableCell align="left">{cat.role}</TableCell>
                <TableCell align="left">{cat.experience}</TableCell>
                <TableCell align="left">
                  <div className="flex flex-wrap w-[200px] gap-1">
                    {cat.skills.map((skill, i) => (
                      <Badge key={i} className="bg-green-500 text-white">{skill}</Badge>
                    ))}
                  </div>
                </TableCell>
                <TableCell align="left">{cat.salary}</TableCell>
                <TableCell align="center">
                    <MoreVertical className="w-5 h-5" />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
      <CardFooter className="flex flex-col items-start gap-2">
        <div className="flex w-full justify-between items-center mt-5">
            <p className="text-sm text-muted-foreground">
              Showing 1-3 of {jobCategories.length} users
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
      </CardFooter>
    </Card>
  );
}