import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MoreVertical, ChevronLeft, ChevronRight } from "lucide-react";
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { Edit, Trash2 } from "lucide-react";
import { useState } from "react";
import EditJobCategoryDialog from "@/dashboard-components/edit-job-category";
import DeleteJobCategoryDialog from "@/dashboard-components/delete-job-category";
import JobCategoryMobTable from "./job-category-mob-table";

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
  const [editJob, setEditJob] = useState<any | null>(null);
  const [deleteJob, setDeleteJob] = useState<any | null>(null);

  return (
    <Card className="w-[95%] !font-inter-regular mt-5">
      <CardHeader>
        <CardTitle className="text-2xl font-poppins-semibold text-left">Job Category Management</CardTitle>
        <CardDescription className="text-left">Manage Job Categories</CardDescription>
      </CardHeader>
      <CardContent>
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
              {jobCategories.map((cat, idx) => (
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
                          onClick={() => setEditJob(cat)}
                        >
                          Edit Job <Edit className="w-5 h-5 text-green-600" />
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="justify-between text-red-600"
                          onClick={() => setDeleteJob(cat)}
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
        {/* Mobile Cards */}
        <div className="block md:hidden">
          {jobCategories.map((cat, idx) => (
            <div key={idx} className="mb-4">
              <JobCategoryMobTable
                job={cat}
                onEdit={() => setEditJob(cat)}
                onDelete={() => setDeleteJob(cat)}
              />
            </div>
          ))}
        </div>
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
      {editJob && (
        <EditJobCategoryDialog
          open={!!editJob}
          onOpenChange={(open: boolean) => !open && setEditJob(null)}
          job={editJob}
          onSave={updatedJob => {
            // handle save logic here
            setEditJob(null);
          }}
        />
      )}
      {/* Delete Dialog */}
      {deleteJob && (
        <DeleteJobCategoryDialog
          open={!!deleteJob}
          onOpenChange={(open: boolean) => !open && setDeleteJob(null)}
          onDelete={() => {
            // handle delete logic here
            setDeleteJob(null);
          }}
        />
      )}
    </Card>
  );
}