import SearchJobCategory from "@/dashboard-components/search-job-category";
import JobCategoryTable from "@/dashboard-components/job-category-table";

export default function JobCategoryManagement() {
    return (
        <div className="flex flex-col items-start justify-start min-h-screen ">
            <SearchJobCategory />
            <JobCategoryTable />
        </div> 
    );
}