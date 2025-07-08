import { Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
    CardFooter,
 } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

type Job ={
    id: number;        
  title: string;    
  description: string; 
  location: string;   
  type: "Full-time" | "Part-time" | "Contract" | "Internship";
  salary: string;      
  postedOn: string;
}

export default function JobCards(props:Job) {
    return(
            <Card className="w-full">
                <CardHeader>
                    <CardTitle className="text-xl font-poppins-semibold text-left">{props.title}</CardTitle>
                    <CardDescription className="font-inter-regular text-left">{props.description}</CardDescription>
                </CardHeader>
                <CardContent className="!font-inter-regular text-left">
                    <div className="flex gap-2"><p className="font-inter-bold text-sm">Location:</p><p className="text-secondary text-sm">{props.location}</p></div>
                    <div className="flex gap-2"><p className="font-inter-bold text-sm">Type</p><p className="text-secondary text-sm">{props.type}</p></div>
                    <div className="flex gap-2"><p className="font-inter-bold text-sm">Salary</p><p className="text-secondary text-sm">{props.salary}</p></div>
                    <div className="bg-green rounded-full inline-block text-sm text-white px-3 py-1 mt-2">Posted on: MM/DD/YY</div>
                </CardContent>
                <CardFooter>
                    <Button className="!bg-blue text-white !font-inter-regular">View Candidates</Button>
                </CardFooter>
            </Card>
    )
}