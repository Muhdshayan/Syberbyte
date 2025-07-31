import SearchJobCategory from "@/dashboard-components/search-job-category";
import { useAuthStore } from "@/Login/useAuthStore";
export default function JobCategoryManagement() {
    const permission = useAuthStore((state) => state.authUser?.permission);
    console.log("User permission:", permission);
    return (
        <div className="flex flex-col w-full h-screen items-start justify-start ">
            <SearchJobCategory />
        </div> 
    );
}