import SearchUser from "@/dashboard-components/search-user";
import UserTable from "@/dashboard-components/user-table";

export default function AdminDashboard() {
    return ( 
        <div className="flex flex-col items-start justify-start min-h-screen ">
            <SearchUser />
            <UserTable />
        </div> 
        
    );  
}