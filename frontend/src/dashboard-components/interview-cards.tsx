import { Card } from "@/components/ui/card";

interface InterviewCardProps {
  name: string;
  time: string;
  role: string;
}

export default function InterviewCards({ name, time, role }: InterviewCardProps) {
  return (
    <Card className="gap-1 font-inter-medium text-left p-4 mb-4">
      <div className="font-medium">{name}</div>
      <div className="text-xs text-muted-foreground">{time}</div>
      <div className="text-sm">{role}</div>
    </Card>
  );
}