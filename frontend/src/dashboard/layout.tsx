// layouts/DashboardLayout.tsx
import { Outlet, useLocation} from "react-router-dom";
import {
  Avatar,
  AvatarFallback,
} from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { Users, Briefcase, BarChart, Brain, LogOut, Mail, Search, FileText } from "lucide-react";
import type React from "react";
import { Link } from "react-router-dom";
import Breadcrumb from "@/dashboard-components/breadcrumb";
import AddUserAdmin from "@/dashboard-components/add-user-admin";
import AddCategory from "@/dashboard-components/add-new-category"



type MenuItem = { label: string; icon: React.ReactNode; to?: string; onClick?: () => void};

const menu: Record<string, MenuItem[]> = {
  admin: [
    { label: "User management", icon: <Users className="w-6 h-6 text-green" />,  to:"/dashboard/admin"},
    { label: "Job category management", icon: <Briefcase className="w-6 h-6 text-green" />, to:"/dashboard/admin/job-category-management" },
    { label: "System health moniter", icon: <BarChart className="w-6 h-6 text-green" />, to:"/dashboard/admin/system-health-monitor" },
    { label: "AI performance metrics", icon: <Brain className="w-6 h-6 text-green" />, to:"/dashboard/admin/ai-performance-metrics" },
    { label: "Sign out", icon: <LogOut className="w-6 h-6 text-green" />, onClick: () => {} },
  ],
  recruiter: [
    { label: "View candidates", icon: <Users className="w-6 h-6 text-green" /> , to:"/dashboard/recruiter/"},
    { label: "Manage Interview", icon: <Search className="w-6 h-6 text-green" />, to:"/dashboard/recruiter/manage-interview" },
    { label: "Email templates", icon: <Mail className="w-6 h-6 text-green" />, to:"/dashboard/recruiter/email-templates" },
    { label: "Sign out", icon: <LogOut className="w-6 h-6 text-green" />, onClick: () => {} },
  ],
  hr: [
    { label: "Active jobs", icon: <Briefcase className="w-6 h-6 text-green" />, to:"/dashboard/hr" },
    { label: "Final interview", icon: <FileText className="w-6 h-6 text-green" />, to:"/dashboard/hr/final-interview" },
    { label: "Email templates", icon: <Mail className="w-6 h-6 text-green" />, to:"/dashboard/hr/email-templates" },
    { label: "Sign out", icon: <LogOut className="w-6 h-6 text-green" />, onClick: () => {} },
  ],
};

const adminTablePages = [
  '/dashboard/admin',
  '/dashboard/admin/job-category-management',
  '/dashboard/admin/',
  '/dashboard/admin/job-category-management/'

];

export default function DashboardLayout() {
   const { pathname } = useLocation();
  // "/dashboard/admin/anything" → ["", "dashboard", "admin", ...]
  const role = pathname.split("/")[2]?.toLowerCase() ?? "hr";
  const items = menu[role] ?? menu.hr;

  const isAdminTablePage = adminTablePages.includes(pathname);


  return (
    <>

      <header className={`${isAdminTablePage? `sticky` : `fixed `} top-0 left-0 flex flex-col w-screen gap-3 bg-cream z-3` }>
        <div className="w-screen overflow-x-hidden auto flex items-center justify-between pl-3 md:pr-6 pr-3 pt-2">
          <div className="flex items-center gap-2 ">
            <img src="/starblack.svg" className="w-6 h-6" />
            <span className="font-inter-medium text-xl">Company Portal</span>
          </div>
          <div className="flex-shrink-0">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Avatar className="h-9 w-9">
                <AvatarFallback>PF</AvatarFallback>
              </Avatar>
            </DropdownMenuTrigger>

            <DropdownMenuContent  align="end" 
            className="w-48 font-inter-regular">
              {items.map(({ label, icon, to }, i) => (
                <div key={label}>
                  {i === items.length - 1 && <DropdownMenuSeparator />}
                  {to ? (
                    <DropdownMenuItem asChild className="flex justify-between items-center gap-5 hover:bg-cream">
                      <Link to={to} className="flex justify-between items-center w-full text-primary">
                        {label}
                        <span>{icon}</span>
                      </Link>
                    </DropdownMenuItem>
                  ) : (
                    <DropdownMenuItem className="flex justify-between items-center gap-5 hover:bg-cream">
                      {label}
                      <span>{icon}</span>
                    </DropdownMenuItem>
                  )}
                </div>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
          </div>
        </div>
        </header>
        {isAdminTablePage ? (
          
          <div className=" flex md:flex-row flex-col items-start pl-3">
             {pathname === "/dashboard/admin" && <AddUserAdmin />}
              {pathname === "/dashboard/admin/job-category-management" && <AddCategory />}
            <div className="flex flex-col flex-1">
              <div className=" pt-5 inline-flex">
                <Breadcrumb/>
              </div>
              <main>
                <Outlet />
              </main>
            </div>
          </div>) : 
          (
          <>
          <div className="relative top-16 flex w-full overflow-x-auto">
            <Breadcrumb/>
          </div>
          <main className="relative top-32 pb-6 w-full overflow-x-auto">
            <Outlet />
          </main>
          </>
          )}   
      
    </>
  );
}
