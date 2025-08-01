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
import { Users, Briefcase, BarChart, Brain, LogOut } from "lucide-react";
import type React from "react";
import { Link } from "react-router-dom";
import Breadcrumb from "@/dashboard-components/breadcrumb";
import AddUserAdmin from "@/dashboard-components/add-user-admin";
import AddCategory from "@/dashboard-components/add-new-category";
import SignOutDialog from "@/dashboard-components/sign-out";
import {useAuthStore} from "@/Login/useAuthStore";

type MenuItem = { label: string; icon: React.ReactNode; to?: string; isSignOut?: boolean; newTab?: boolean;};

const menu: Record<string, MenuItem[]> = {
  admin: [
    { label: "User management", icon: <Users className="w-6 h-6 text-green" />,  to:"/dashboard/admin"},
    { label: "Job category management", icon: <Briefcase className="w-6 h-6 text-green" />, to:"/dashboard/admin/job-category-management" },
    { label: "System health moniter", icon: <BarChart className="w-6 h-6 text-green" />, to:"http://localhost:3000/d/Kbq9jQmiz/docker-and-system-monitoring", newTab:true },
    { label: "Sign out", icon: <LogOut className="w-6 h-6 text-green" />, isSignOut: true },
  ],
  recruiter: [
    { label: "View candidates", icon: <Users className="w-6 h-6 text-green" /> , to:"/dashboard/recruiter/"},
    { label: "Sign out", icon: <LogOut className="w-6 h-6 text-green" />, isSignOut: true },
  ],
  hr: [
    { label: "Active jobs", icon: <Briefcase className="w-6 h-6 text-green" />, to:"/dashboard/hr_manager" },
    { label: "Sign out", icon: <LogOut className="w-6 h-6 text-green" />, isSignOut: true },
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
  const { authUser } = useAuthStore(); // Get the current user from the auth store
  const role = pathname.split("/")[2]?.toLowerCase() ?? "hr";
  const items = menu[role] ?? menu.hr;

  const permission = authUser?.permission ?? 0; // Get the user's permission level

  // Filter menu items based on permission
  const filteredItems = items.filter(
    (item) =>
      !(permission === 5 && (item.label === "System health moniter" || item.label === "AI performance metrics"))
  );

  const isAdminTablePage = adminTablePages.includes(pathname);

  return (
    <>
      <header className={`relative top-0 left-0 flex flex-col w-screen gap-3 bg-cream z-3`}>
        <div className="w-screen overflow-x-hidden auto flex items-center justify-between px-3 pt-2">
          <div className="flex items-center gap-2 ">
            <img src="/starblack.svg" className="w-6 h-6" />
            <span className="font-inter-medium text-xl">Company Portal</span>
          </div>
          <div className="flex-shrink-0">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Avatar className="h-9 w-9 cursor-pointer">
                  <AvatarFallback>PF</AvatarFallback>
                </Avatar>
              </DropdownMenuTrigger>

              <DropdownMenuContent align="end" className="w-48 font-inter-regular">
                {filteredItems.map(({ label, icon, to, isSignOut, newTab }, i) => (
                  <div key={label}>
                    {i === filteredItems.length - 1 && <DropdownMenuSeparator />}
                    {isSignOut ? (
                      <SignOutDialog>
                        <div className="flex justify-between items-center w-full px-2 py-1.5 text-sm cursor-pointer hover:bg-cream rounded-sm">
                          {label}
                          <span>{icon}</span>
                        </div>
                      </SignOutDialog>
                    ) : to ? (
                      <DropdownMenuItem
                        asChild
                        className="flex justify-between items-center gap-5 hover:bg-cream"
                      >
                        {newTab ? (
                          <a
                            href={to}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex justify-between items-center w-full text-primary"
                          >
                            {label}
                            <span>{icon}</span>
                          </a>
                        ) : (
                          <Link
                            to={to}
                            className="flex justify-between items-center w-full text-primary"
                          >
                            {label}
                            <span>{icon}</span>
                          </Link>
                        )}
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
        <div className="flex md:flex-row flex-col justify-between w-full items-start">
          {pathname === "/dashboard/admin" && <AddUserAdmin />}
          {pathname === "/dashboard/admin/job-category-management" && <AddCategory />}
          <div className="flex flex-col flex-1">
            <div className="pt-5 inline-flex">
              <Breadcrumb />
            </div>
            <main>
              <Outlet />
            </main>
          </div>
        </div>
      ) : (
        <>
          <main className="mt-5 flex flex-col items-start justify-start w-full overflow-x-hidden">
            <div className="ml-4">
              <Breadcrumb />
            </div>
            <Outlet />
          </main>
        </>
      )}
    </>
  );
}