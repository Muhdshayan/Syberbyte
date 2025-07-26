import SearchUser from "@/dashboard-components/search-user";

export default function AdminDashboard() {
    return ( 
        <div className="flex flex-col md:items-start items-center md:justify-start justify-center">
            <SearchUser />
        </div> 
        
    );  
}