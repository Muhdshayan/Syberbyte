import SearchUser from "@/dashboard-components/search-user";
import UserTable from "@/dashboard-components/user-table";
import { useLocation } from "react-router-dom";
import SearchJobCategory from "@/dashboard-components/search-job-category";
import JobCategoryTable from "@/dashboard-components/job-category-table";

export default function AdminDashboard() {
    const { pathname } = useLocation();
    return ( 
         pathname === "/dashboard/admin"  ? 
        (<div className="flex flex-col items-start justify-start min-h-screen ">
            <SearchUser />
            <UserTable />
        </div> ):( 
        <div className="flex flex-col items-start justify-start min-h-screen ">
            <SearchJobCategory />
            <JobCategoryTable />
        </div>)  
    );  
}