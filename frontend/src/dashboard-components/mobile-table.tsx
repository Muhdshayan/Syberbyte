import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { MoreVertical } from "lucide-react";
interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  status: UserStatus;
  lastActive: string;
}
type UserStatus = "Active" | "Suspended";
type UserRole = "Admin" | "HR Manager" | "Recruiter";



export default function MobileTable(props: User) {
    return(
        <Card className="w-full p-5 font-inter-regular">
            <div className="flex flex-row justify-between items-center">
                    <div className="flex items-center gap-3">
                        <Avatar className="h-8 w-8">
                          <AvatarFallback>
                            {props.name
                              .split(" ")
                              .map((n) => n[0])
                              .join("")
                              .toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                       <p className="text-sm text-left font-medium">{props.name}</p>
                       <p className="text-xs text-left text-muted-foreground">{props.email}</p>
                     </div>
                   </div>
                   <div><MoreVertical/></div>
                   </div>
                   <div className="flex flex-col justify-center items-center w-full">
                    <div className="flex flex-row justify-between w-full"><p>Role</p><Badge variant="outline">{props.role}</Badge></div>
                    <div className="flex flex-row justify-between w-full mt-2"><p>status</p><Badge
                     className={
                       props.status === "Active"
                         ? "bg-green-100 text-green-700"
                         : "bg-red-100 text-red-700"
                     }
                   >
                     {props.status}
                   </Badge></div>
                    <div className="flex flex-row justify-between w-full"><p>Last Active</p><span>{props.lastActive}</span></div>
                   </div>
            </Card>
    )
}