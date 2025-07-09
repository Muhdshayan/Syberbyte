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
export default function AddUserAdmin() {
    return (
        <div className="md:w-[25%] w-full bg-cream shadow-none !font-inter-regular py-5 ">
            <CardHeader>
                <CardTitle className="text-2xl font-poppins-semibold text-left">Add new User</CardTitle>
            </CardHeader>
            <CardContent className="!font-inter-regular mt-6">
                <Label htmlFor="name">Full Name</Label>
                <Input id="name" placeholder="Enter name" className="w-full mb-2 mt-4 bg-white" /> 
                <div className="text-secondary text-sm text-left">enter your full name</div>   
                <Label htmlFor="email" className="mt-4">Email Adress</Label>
                <Input id="email" placeholder="Enter email" className="w-full mb-2 mt-4 bg-white" />
                <div className="text-secondary text-sm text-left">enter your email address</div>
                <Label htmlFor="role" className="my-4">Role</Label>  
                <DropdownMenu>
                    <DropdownMenuTrigger asChild >
                        <Button variant="outline" className="w-full !text-left !text-sm font-inter-regular !border-gray-200 !bg-white">

                            Select Role
                            <ChevronDown className="ml-auto h-4 w-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-48 font-inter-regular" align="start">
                        <DropdownMenuItem>Admin</DropdownMenuItem>
                        <DropdownMenuItem>HR</DropdownMenuItem>
                        <DropdownMenuItem>Recruiter</DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
                 <Label htmlFor="password" className="mt-4">Password</Label>
                <Input id="password" type="password" placeholder="password" className="w-full mb-2 mt-4 bg-white" />
                <div className="text-secondary text-sm text-left">enter your password</div>
            </CardContent>
            <CardFooter className="mt-6 flex flex-col gap-5">
                <Button className="w-full !bg-blue"><Plus className="w-4 h-4"/> Create User </Button>
                <div className=" font-inter-medium bg-green rounded-lg w-full text-white text-left p-5">
                    Quick States
                    <div className="mt-1 w-full flex justify-between font-inter-regular text-sm">
                        <p>Total user</p><p>46</p>
                    </div>
                    <div className="mt-1 w-full flex justify-between font-inter-regular text-sm">
                        <p>Active Users</p><p>22</p>
                    </div>
                    <div className="mt-1 w-full flex justify-between font-inter-regular text-sm">
                        <p>Suspended</p><p>03</p>
                    </div>
                </div>
            </CardFooter>
            
        </div>
    )
}