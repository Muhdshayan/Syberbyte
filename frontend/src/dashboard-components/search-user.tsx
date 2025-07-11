import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Search } from "lucide-react"
import { Input } from "@/components/ui/input";
export default function SearchUser() {
    return (
        <div className="flex flex-col items-start mt-5 justify-start w-full !font-inter-regular">
            <Card className="w-[95%] p-3 flex md:flex-row flex-col justify-between">
                <div className="flex gap-2">
                    <div className="relative z-1">
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                            <Search className="h-5 w-5" />
                        </span>
                        <Input
                            placeholder="Search by name or email"
                            className="pl-10" // Add left padding for the icon
                        />
                    </div>
                    <div>
                        <Button className="!bg-primary"><Search className="h-5 w-5" /></Button>
                    </div>
                    </div>
                    <div className=" flex md:gap-2 gap-1">
                    <Button className="!bg-blue !text-sm !font-inter-regular !px-2">Admin</Button>
                    <Button className="!bg-blue !text-sm !font-inter-regular !px-2">Recruiter</Button>
                    <Button className="!bg-blue !text-sm !font-inter-regular !px-2">Hr Manager</Button>
                    <Button className="!bg-green !text-sm !font-inter-regular !px-2">All Users</Button>
                    </div>
            </Card>
        </div>
    );
}