import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MoreVertical, ChevronLeft, ChevronRight } from "lucide-react";
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { Edit, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import EditJobCategoryDialog from "@/dashboard-components/edit-job-category";
import DeleteJobCategoryDialog from "@/dashboard-components/delete-job-category";
import JobCategoryMobTable from "./job-category-mob-table";
import { useAdminStore } from "@/dashboard/adminDashboard/admin-store";
import type { JobCategory } from "@/dashboard/adminDashboard/admin-store";


export default function JobCategoryTable() {
  const jobCategories = useAdminStore((state) => state.jobCategories);
  const editCategory = useAdminStore((state) => state.editCategory);
  const deleteCategory = useAdminStore((state) => state.deleteCategory);
  const [editJob, setEditJob] = useState<JobCategory | null>(null);
  const [deleteJob, setDeleteJob] = useState<JobCategory | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const categoriesPerPage = 3;
  const fetchJobCategories = useAdminStore((state) => state.fetchJobCategories);
  useEffect(() => {
    fetchJobCategories();
  }
  , [fetchJobCategories]);

  const indexOfLastCategory = currentPage * categoriesPerPage;
  const indexOfFirstCategory = indexOfLastCategory - categoriesPerPage;
  const currentCategories = Array.isArray(jobCategories)
    ? jobCategories.slice(indexOfFirstCategory, indexOfLastCategory)
    : [];
  const totalPages = Math.ceil(jobCategories.length / categoriesPerPage);


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
              {currentCategories.map((cat, idx) => (
                <TableRow key={idx}>
                  <TableCell align="left">{cat.industry}</TableCell>
                  <TableCell align="left">{cat.role}</TableCell>
                  <TableCell align="left">{cat.experience}</TableCell>
                  <TableCell align="left">
                    <div className="flex flex-wrap w-[200px] gap-1">
                       {(Array.isArray(cat.skills) ? cat.skills : String(cat.skills).split(",").map(s => s.trim())).map((skill, i) => (
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
              <JobCategoryMobTable
                jobs={currentCategories}
                onEdit={cat => setEditJob(cat)}
                onDelete={cat => setDeleteJob(cat)}
              />
        </div>
      </CardContent>
      <CardFooter className="flex flex-col items-start gap-2 w-full">
        <div className="flex justify-between items-center mt-5 w-full">
          <p className="text-sm text-muted-foreground">
            Showing {indexOfFirstCategory + 1}-{Math.min(indexOfLastCategory, jobCategories.length)} of {jobCategories.length} Categories
          </p>
          <div className="flex gap-2">
            <Button
              className="!bg-blue"
              onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft />
            </Button>
            <Button
              className="!bg-blue"
              onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
            >
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
          onSave={(updatedJob) => {
            editCategory(updatedJob);
            console.log("Final job data:", updatedJob);

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
            deleteCategory(deleteJob.role);
            setDeleteJob(null);
          }}
        />
      )}
    </Card>
  );
}