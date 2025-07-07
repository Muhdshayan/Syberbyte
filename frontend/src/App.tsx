<<<<<<< HEAD
import { Button } from "@/components/ui/button";
import { useState } from "react";

function App() {
  const [response, setResponse] = useState("");

  const updateResponse = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/hello-world/");
      const data = await res.json();
      setResponse(data["message"]);
    } catch (error) {
      console.error("Error fetching time:", error);
      setResponse("Failed to fetch time");
    }
  };

  return (
    <div className="flex min-h-svh flex-col items-center justify-center space-y-4">
      <Button onClick={updateResponse}>Click me to see Time</Button>
      <div className="text-lg font-medium text-center text-primary">{response}</div>
    </div>
  );
}

export default App;
=======
import Login from "./Login/Login"
import AdminDashboard from "./dashboard/adminDashboard/dashboard"
import HrDashboard from "./dashboard/HrDashboard/dashboard"
import RecruiterDashboard from "./dashboard/RecruiterDashboard/dashboard"
import DashboardLayout from "./dashboard/layout"
import JobCategoryManagement from "./dashboard/adminDashboard/job-category-management"
import SystemHealthMonitor from "./dashboard/adminDashboard/system-health-monitor"
import AiPerformanceMetrics from "./dashboard/adminDashboard/ai-performance-metrics"
import ActiveJobs from "./dashboard/HrDashboard/dashboard"
import FinalInterview from "./dashboard/HrDashboard/final-interview"
import EmailTemplatesHr from "./dashboard/HrDashboard/email-templates-hr"
import ViewCandidates from "./dashboard/RecruiterDashboard/dashboard"
import InitialScreening from "./dashboard/RecruiterDashboard/initial-screening"
import EmailTemplatesRecruit from "./dashboard/RecruiterDashboard/email-templates-recruiter"
import './App.css'
import { Route, Routes } from "react-router-dom"

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Login/>} />
        <Route path="/dashboard" element={<DashboardLayout/>}>
           <Route path="admin">
             <Route index element={<AdminDashboard/>} />
             <Route path="job-category-management" element={<JobCategoryManagement/>} />
             <Route path="system-health-monitor" element={<SystemHealthMonitor/>} />
              <Route path="ai-performance-metrics" element={<AiPerformanceMetrics/>} />
           </Route>
          <Route path="hr">
            <Route index element={<ActiveJobs/>} />
            <Route path="final-interview" element={<FinalInterview/>} />
            <Route path="email-templates-hr" element={<EmailTemplatesHr/>} />
          </Route>
          <Route path="recruiter">
            <Route index element={<ViewCandidates/>} />
            <Route path="initial-screening" element={<InitialScreening/>} />
            <Route path="email-templates-recruiter" element={<EmailTemplatesRecruit/>} />
          </Route>
        </Route>
        </Routes>
    </>
  )
}

export default App
>>>>>>> origin/Frontend/Rida
