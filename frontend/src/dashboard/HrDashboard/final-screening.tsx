import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, ShieldCheck, Brain, LayoutGrid } from "lucide-react";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { useHrStore } from "./hr-store";

import {  useEffect } from "react"; 

const candidates = [
  {
    name: "Alex",
    technical: 95,
    communication: 88,
    problemSolving: 94,
  },
  {
    name: "Micheal",
    technical: 72,
    communication: 78,
    problemSolving: 80,
  },
  {
    name: "Sarah",
    technical: 90,
    communication: 92,
    problemSolving: 85,
  },
];

const analyticsData = [
  {
    icon: <Users className="w-5 h-5" />,
    title: "Diversity Analytics",
    stats: [
      { value: "38%", label: "Gender Diversity" },
      { value: 27, label: "Average Age" },
      { value: 5, label: "Countries" },
    ],
    alert: "Potential Bias Alert: Name-based bias detected in 2 evaluations",
  },
  {
    icon: <ShieldCheck className="w-5 h-5" />,
    title: "Bias Detection",
    stats: [
      { value: "97%", label: "Fair Evaluation" },
      { value: 1, label: "Raised Flags" },
    ],
    alert: "Potential Bias Alert: Name-based bias detected in 1 evaluation",
  },
  {
    icon: <Brain className="w-5 h-5" />,
    title: "AI Hiring Recommendations",
    stats: [
      { value: 2, label: "Recommended" },
      { value: 1, label: "Further Review" },
      { value: 3, label: "Not Recommended" },
    ],
    alert: "Potential Bias Alert: Name-based bias detected in 1 evaluation",
  },
];

interface Stat {
  value: string | number;
  label: string;
}

interface AnalyticsCardProps {
  icon: React.ReactNode;
  title: string;
  stats: Stat[];
  alert: string;
}

function AnalyticsCard({ icon, title, stats, alert }: AnalyticsCardProps) {
  return (
    <Card className="w-full shadow min-w-[250px]">
      <CardHeader className="flex flex-row items-center gap-2">
        {icon}
        <CardTitle className="text-lg font-semibold break-words">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between text-sm mb-2 flex-wrap gap-2">
          {stats.map((stat, idx) => (
            <div key={idx} className="min-w-[80px] max-w-[110px]">
              <div className="font-bold text-lg break-words">{stat.value}</div>
              <div className="text-muted-foreground text-xs break-words">{stat.label}</div>
            </div>
          ))}
        </div>
        <Badge className="bg-green text-white w-full justify-center py-2 mt-2 break-words whitespace-normal text-xs">
          {alert}
        </Badge>
      </CardContent>
    </Card>
  );
}

export default function FinalScreeningPage() {


  const { candidates } = useHrStore((state) => ({candidates: state.candidates,}));
  const fetchCandidates = useHrStore((state) => state.fetchCandidates);

    useEffect(() => {
      fetchCandidates();
    }, []);

  return (
        <div className="p-4 w-screen flex flex-col gap-4">
          <div className=" grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analyticsData.map((card) => (
              <AnalyticsCard
                key={card.title}
                icon={card.icon}
                title={card.title}
                stats={card.stats}
                alert={card.alert}
              />
            ))}
            </div>
      {/* Comparison Matrix Table */}
      <Card className="w-full shadow">
        <CardHeader className="flex flex-row items-center gap-2 pb-2">
          <LayoutGrid className="w-5 h-5" />
          <CardTitle className="text-lg font-semibold">Comparison Matrix</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="font-semibold">No</TableHead>
                <TableHead className="font-semibold">Technical</TableHead>
                <TableHead className="font-semibold">Experience</TableHead>
                <TableHead className="font-semibold">Cultural</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {candidates.map((c, idx) => (
                <TableRow key={c.id ?? idx}>
                  <TableCell>{c.name}</TableCell>
                  <TableCell>{c.breakdown.technical}</TableCell>
                  <TableCell>{c.breakdown.experience}</TableCell>
                  <TableCell>{c.breakdown.cultural}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      
    </div>
  );
}