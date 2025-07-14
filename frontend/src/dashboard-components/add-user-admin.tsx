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
  role: z.enum(["Admin", "HR Manager", "Recruiter"]),
  password: z.string().min(5, "Password must be at least 5 characters"),
});
type NewUser = z.infer<typeof newUserSchema>;

export default function AddUserAdmin() {
  const [form, setForm] = useState<NewUser>({
    name: "",
    email: "",
    role: "Admin",
    password: "",
  });
  const [roleOpen, setRoleOpen] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.id]: e.target.value });
  };

  const handleRoleSelect = (role: NewUser["role"]) => {
    setForm((prev) => ({ ...prev, role }));
    setRoleOpen(false);
  };

  const addUser = useAdminStore((state) => state.addUser);
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = newUserSchema.safeParse(form);
    console.log(result)
    if (!result.success) {
     toast.error(result.error.errors[0].message); // Show toast on zod error
      return;
    }
    await addUser(form);
    setForm({ name: "", email: "", role: "Admin", password: "" });
  };

  const users = useAdminStore((state) => state.users);
  const stats = getUserStats(users);

  return (
    <form
      className="md:w-[25%] w-full bg-cream shadow-none !font-inter-regular py-5"
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
          className="w-full mb-2 mt-4 bg-white"
        />
        <div className="text-secondary text-sm text-left">enter your full name</div>
        <Label htmlFor="email" className="mt-4">
          Email Address
        </Label>
        <Input
          id="email"
          value={form.email}
          onChange={handleChange}
          placeholder="Enter email"
          className="w-full mb-2 mt-4 bg-white"
        />
        <div className="text-secondary text-sm text-left">enter your email address</div>
        <Label htmlFor="role" className="my-4">
          Role
        </Label>
        <DropdownMenu open={roleOpen} onOpenChange={setRoleOpen}>
          <DropdownMenuTrigger asChild>
            <Button
              type="button"
              variant="outline"
              className="w-full !text-left !text-sm font-inter-regular !border-gray-200 !bg-white"
            >
              {form.role}
              <ChevronDown className="ml-auto h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-48 font-inter-regular" align="start">
            <DropdownMenuItem onClick={() => handleRoleSelect("Admin")}>Admin</DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleRoleSelect("HR Manager")}>HR</DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleRoleSelect("Recruiter")}>Recruiter</DropdownMenuItem>
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
          className="w-full mb-2 mt-4 bg-white"
        />
        <div className="text-secondary text-sm text-left">enter your password</div>
      </CardContent>
      <CardFooter className="mt-6 flex flex-col gap-5">
        <Button type="submit" className="w-full !bg-blue">
          <Plus className="w-4 h-4" /> Create User
        </Button>
        <div className="font-inter-medium bg-green rounded-lg w-full text-white text-left p-5">
          Quick States
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