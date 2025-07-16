import Login from "./Login/Login"
import AdminDashboard from "./dashboard/adminDashboard/dashboard"
import DashboardLayout from "./dashboard/layout"
import SystemHealthMonitor from "./dashboard/adminDashboard/system-health-monitor"
import AiPerformanceMetrics from "./dashboard/adminDashboard/ai-performance-metrics"
import ActiveJobs from "./dashboard/HrDashboard/dashboard"
import FinalInterview from "./dashboard/HrDashboard/final-interview"
import ViewCandidates from "./dashboard/RecruiterDashboard/dashboard"
import InitialScreeningPage from "./dashboard/RecruiterDashboard/initial-screening"
import JobCategoryManagement from "@/dashboard/adminDashboard/job-category-management"
import AddJob from "./dashboard/HrDashboard/add-job"
import './App.css'
import { Route, Routes } from "react-router-dom"
import ManageInterview from "@/dashboard/RecruiterDashboard/manage-interview"
import { Toaster } from "sonner";

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
          <Route path="hr_manager">
            <Route index element={<ActiveJobs/>} />
            <Route path="add-job" element={<AddJob/>} />
            <Route path="final-interview" element={<FinalInterview/>} />
          </Route>
          <Route path="recruiter">
            <Route index element={<ViewCandidates/>} />
            <Route path=":JobId/Initial-Screening" element={<InitialScreeningPage/>} />
            <Route path="manage-interview" element={<ManageInterview/>} />
          </Route>
        </Route>
        </Routes>
        <Toaster position="top-right" />
    </>
  )
}

export default App
