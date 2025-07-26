import { useEffect, useState, useRef } from "react";
import {
  Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter,
} from "@/components/ui/card";
import {
  Table, TableHeader, TableRow, TableHead, TableBody, TableCell,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MoreVertical, ChevronLeft, ChevronRight, Edit, Trash2 } from "lucide-react";
import {
  DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import EditJobCategoryDialog from "@/dashboard-components/edit-job-category";
import DeleteJobCategoryDialog from "@/dashboard-components/delete-job-category";
import JobCategoryMobTable from "./job-category-mob-table";
import { useAdminStore } from "@/dashboard/adminDashboard/admin-store";
import type { JobCategory } from "@/dashboard/adminDashboard/admin-store";

export default function JobCategoryTable({ categories }: { categories: JobCategory[] }) {
  const editCategory = useAdminStore((state) => state.editCategory);
  const deleteCategory = useAdminStore((state) => state.deleteCategory);
  const fetchJobCategories = useAdminStore((state) => state.fetchJobCategories);

  const [editJob, setEditJob] = useState<JobCategory | null>(null);
  const [deleteJob, setDeleteJob] = useState<JobCategory | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [categoriesPerPage, setCategoriesPerPage] = useState(4);
  const tableBodyRef = useRef<HTMLTableSectionElement | null>(null);

  useEffect(() => {
    fetchJobCategories();
  }, [fetchJobCategories]);

  useEffect(() => {
    setCurrentPage(1);
  }, [categories]);

  // Dynamically adjust number of rows to fit within 600px
  useEffect(() => {
    const maxHeight = 500;
    const sampleRow = tableBodyRef.current?.querySelector("tr");
    if (sampleRow) {
      const rowHeight = sampleRow.getBoundingClientRect().height;
      const newLimit = Math.floor(maxHeight / rowHeight);
      if (newLimit && newLimit !== categoriesPerPage) {
        setCategoriesPerPage(newLimit);
      }
    }
  }, [categories, categoriesPerPage]);

  const indexOfLastCategory = currentPage * categoriesPerPage;
  const indexOfFirstCategory = indexOfLastCategory - categoriesPerPage;
  const currentCategories = categories.slice(indexOfFirstCategory, indexOfLastCategory);
  const totalPages = Math.ceil(categories.length / categoriesPerPage);

  return (
    <Card className="w-[99%] min-h-[750px] justify-between !font-inter-regular my-5">
      <div className="flex flex-col gap-4">
        <CardHeader>
          <CardTitle className="text-2xl font-poppins-semibold text-left">Job Category Management</CardTitle>
          <CardDescription className="text-left">Manage Job Categories</CardDescription>
        </CardHeader>

        <CardContent>
          {/* Desktop Table */}
          <div className="hidden md:block w-full">
            <Table className="w-full">
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[10%]">Industry</TableHead>
                  <TableHead className="w-[10%]">Role</TableHead>
                  <TableHead className="w-[10%]">Experience</TableHead>
                  <TableHead className="w-[10%]">Skills</TableHead>
                  <TableHead className="w-[10%]">Education</TableHead>
                  <TableHead className="w-[10%]">Salary</TableHead>
                  <TableHead className="w-[10%]">Job Type</TableHead>
                  <TableHead className="w-[10%]">Status</TableHead>
                  <TableHead className="w-[10%]">Location</TableHead>
                  <TableHead className="w-[10%]">Actions</TableHead>
                </TableRow>
              </TableHeader>

              <TableBody ref={tableBodyRef}>
                {currentCategories.map((cat, idx) => (
                  <TableRow key={idx}>
                    <TableCell className="max-w-[100px] break-words whitespace-normal">{cat.industry}</TableCell>
                    <TableCell className="max-w-[100px] break-words whitespace-normal">{cat.role}</TableCell>
                    <TableCell className="max-w-[100px] break-words whitespace-normal">{cat.experience_level}</TableCell>
                    <TableCell className="max-w-[100px] px-2 break-words whitespace-normal">
                      <div className="flex flex-wrap gap-1 w-full">
                        {(Array.isArray(cat.skills)
                          ? cat.skills
                          : String(cat.skills).split(",").map(s => s.trim())
                        ).map((skill, i) => (
                          <Badge key={i} className="bg-green text-white">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell className="max-w-[100px] break-words whitespace-normal">{cat.education_level}</TableCell>
                    <TableCell className="max-w-[100px] break-words whitespace-normal">{cat.salary}</TableCell>
                    <TableCell className="max-w-[100px] break-words whitespace-normal">{cat.job_type}</TableCell>
                    <TableCell className="max-w-[150px] px-2 break-words whitespace-normal">
                      <Badge className={`text-white ${cat.is_active ? "bg-green" : "bg-red-500"}`}>
                        {cat.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </TableCell>
                    <TableCell className="max-w-[100px] break-words whitespace-normal">{cat.location}</TableCell>
                    <TableCell className="truncate max-w-[100px] text-center">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <MoreVertical className="w-5 h-5 cursor-pointer" />
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
              onEdit={setEditJob}
              onDelete={setDeleteJob}
            />
          </div>
        </CardContent>
      </div>

      <CardFooter className="flex flex-col items-end gap-2 w-full pb-5">
        <div className="flex justify-between items-center mt-5 w-full">
          <p className="text-sm text-muted-foreground">
            Showing {indexOfFirstCategory + 1}-{Math.min(indexOfLastCategory, categories.length)} of {categories.length} Categories
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

      {/* Dialogs */}
      {editJob && (
        <EditJobCategoryDialog
          open={!!editJob}
          onOpenChange={(open: boolean) => !open && setEditJob(null)}
          job={editJob}
          onSave={(updatedJob) => {
            editCategory(updatedJob);
            setEditJob(null);
          }}
        />
      )}
      {deleteJob && (
        <DeleteJobCategoryDialog
          open={!!deleteJob}
          onOpenChange={(open: boolean) => !open && setDeleteJob(null)}
          jobId={deleteJob.job_id}
          onDelete={() => setDeleteJob(null)}
        />
      )}
    </Card>
  );
}
