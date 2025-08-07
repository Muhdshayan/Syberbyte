import { CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { ChevronDown, Plus } from "lucide-react";
import { z } from "zod";
import { useState } from "react";
import { useAdminStore, getUserStats } from "@/dashboard/adminDashboard/admin-store";
import { toast } from "sonner";

// Zod schema and TypeScript type
const newUserSchema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Invalid email"),
  role: z.enum(["full_admin", "advanced_admin", "basic_admin", "hr_manager", "recruiter"]),
  password: z.string().min(5, "Password must be at least 5 characters"),
  permission: z.number().default(1),
});
type NewUser = z.infer<typeof newUserSchema>;

// Role choices type
type RoleChoice = {
  value: NewUser["role"];
  label: string;
};

// Role choices mapping for display
const ROLE_CHOICES: RoleChoice[] = [
  { value: "full_admin", label: "Full Admin" },
  { value: "advanced_admin", label: "Advanced Admin" },
  { value: "basic_admin", label: "Basic Admin" },
  { value: "hr_manager", label: "HR Manager" },
  { value: "recruiter", label: "Recruiter" },
];

export default function AddUserAdmin() {
  const [form, setForm] = useState<NewUser>({
    name: "",
    email: "",
    role: "recruiter",
    password: "",
    permission: 1,
  });
  const [roleOpen, setRoleOpen] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.id]: e.target.value });
  };

  const handleRoleSelect = (role: NewUser["role"]) => {
    const rolePermissionMap: Record<NewUser["role"], number> = {
      full_admin: 10,
      advanced_admin: 7,
      basic_admin: 5,
      hr_manager: 3,
      recruiter: 1,
    };

    setForm((prev) => ({
      ...prev,
      role,
      permission: rolePermissionMap[role],
    }));

    setRoleOpen(false);
  };

  const addUser = useAdminStore((state) => state.addUser);
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = newUserSchema.safeParse(form);
    console.log(result);
    if (!result.success) {
      toast.error(result.error.errors[0].message);
      return;
    }
    await addUser(form);
    setForm({ name: "", email: "", role: "recruiter", password: "", permission: 1 });
  };

  const users = useAdminStore((state) => state.users);
  const stats = getUserStats(users);

  return (
    <form
      className="md:w-[25%] w-full justify-between bg-cream shadow-none !font-inter-regular pt-5"
      onSubmit={handleSubmit}
    >
      <CardHeader>
        <CardTitle className="text-2xl font-poppins-semibold text-left">Add new User</CardTitle>
      </CardHeader>
      <CardContent className="!font-inter-regular mt-6">
        <Label htmlFor="name">Full Name</Label>
        <Input
          id="name"
          value={form.name}
          onChange={handleChange}
          placeholder="Enter name"
          className="w-full mb-2 mt-1 bg-white"
        />
        <Label htmlFor="email" className="mt-4">
          Email Address
        </Label>
        <Input
          id="email"
          value={form.email}
          onChange={handleChange}
          placeholder="Enter email"
          className="w-full mb-2 mt-1 bg-white"
        />
        <Label htmlFor="role" className="mb-2">
          Role 
        </Label>
        <DropdownMenu open={roleOpen} onOpenChange={setRoleOpen}>
          <DropdownMenuTrigger asChild>
            <Button
              type="button"
              variant="outline"
              className="w-full !text-left !text-sm font-inter-regular !border-gray-200 !bg-white"
            >
              {ROLE_CHOICES.find((choice) => choice.value === form.role)?.label || form.role}
              <ChevronDown className="ml-auto h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-48 font-inter-regular" align="start">
            {ROLE_CHOICES.map((choice) => (
              <DropdownMenuItem key={choice.value} onClick={() => handleRoleSelect(choice.value)}>
                {choice.label}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
        <Label htmlFor="password" className="mt-4">
          Password
        </Label>
        <Input
          id="password"
          type="password"
          value={form.password}
          onChange={handleChange}
          placeholder="password"
          className="w-full mb-2 mt-1 bg-white"
        />
      </CardContent>
      <CardFooter className="mt-6 flex flex-col gap-5">
        <Button type="submit" className="w-full !bg-blue">
          <Plus className="w-4 h-4" /> Create User
        </Button>
        <div className="font-inter-medium bg-green rounded-lg w-full text-white text-left p-5">
          Quick Stats
          <div className="mt-1 w-full flex justify-between font-inter-regular text-sm">
            <p>Total user</p>
            <p>{stats.total}</p>
          </div>
          <div className="mt-1 w-full flex justify-between font-inter-regular text-sm">
            <p>Active Users</p>
            <p>{stats.active}</p>
          </div>
          <div className="mt-1 w-full flex justify-between font-inter-regular text-sm">
            <p>Suspended</p>
            <p>{stats.suspended}</p>
          </div>
        </div>
      </CardFooter>
    </form>
  );
}