import Login from "./Login/Login"
import AdminDashboard from "./dashboard/adminDashboard/dashboard"
import DashboardLayout from "./dashboard/layout"
import SystemHealthMonitor from "./dashboard/adminDashboard/system-health-monitor"
import AiPerformanceMetrics from "./dashboard/adminDashboard/ai-performance-metrics"
import ActiveJobs from "./dashboard/HrDashboard/dashboard"
import FinalInterview from "./dashboard/HrDashboard/final-interview"
import EmailTemplatesHr from "./dashboard/HrDashboard/email-templates-hr"
import ViewCandidates from "./dashboard/RecruiterDashboard/dashboard"
import InitialScreeningPage from "./dashboard/RecruiterDashboard/initial-screening"
import EmailTemplatesRecruit from "./dashboard/RecruiterDashboard/email-templates-recruiter"
import JobCategoryManagement from "@/dashboard/adminDashboard/job-category-management"
import './App.css'
import { Route, Routes, Navigate } from "react-router-dom"
import ManageInterview from "@/dashboard/RecruiterDashboard/manage-interview"
import { Toaster } from "sonner";
import { useAuthStore } from "@/Login/useAuthStore" // Update with your actual store path
import FinalScreeningPage from "./dashboard/HrDashboard/final-screening"
import AddJob from "./dashboard/HrDashboard/add-job"
import Loading from "./dashboard-components/loading"

// Protected Route Component
function ProtectedRoute({ children, requiredPermission }: { children: React.ReactNode, requiredPermission: number }) {
  const { authUser } = useAuthStore();
  
  if (!authUser) {
    return <Navigate to="/" replace />;
  }
  
  if (authUser.permission < requiredPermission) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return <>{children}</>;
}

// Permission-based dashboard redirect
function DashboardRedirect() {
  const { authUser } = useAuthStore();
  
  if (!authUser) {
    return <Navigate to="/" replace />;
  }
  
  // Redirect based on permission level
  if (authUser.permission === 1) {
    return <Navigate to="/dashboard/recruiter" replace />;
  } else if (authUser.permission === 3) {
    return <Navigate to="/dashboard/hr_manager" replace />;
  } else if (authUser.permission >= 5) {
    return <Navigate to="/dashboard/admin" replace />;
  }
  
  return <Navigate to="/" replace />;
}

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Login/>} />
        <Route path="/nothing-to-show" element={ <Loading />} />
        <Route path="/dashboard" element={<DashboardLayout/>}>
          {/* Default dashboard route - redirects based on permission */}
          <Route index element={<DashboardRedirect />} />
          
          {/* Admin Routes */}
          <Route path="admin">
            <Route index element={
              <ProtectedRoute requiredPermission={5}>
                <AdminDashboard/>
              </ProtectedRoute>
            } />
            <Route path="job-category-management" element={
              <ProtectedRoute requiredPermission={7}>
                <JobCategoryManagement/>
              </ProtectedRoute>
            } />
            <Route path="system-health-monitor" element={
              <ProtectedRoute requiredPermission={10}>
                <SystemHealthMonitor/>
              </ProtectedRoute>
            } />
            <Route path="ai-performance-metrics" element={
              <ProtectedRoute requiredPermission={10}>
                <AiPerformanceMetrics/>
              </ProtectedRoute>
            } />
          </Route>
          
          {/* HR Manager Routes */}
          <Route path="hr_manager">
            <Route index element={
              <ProtectedRoute requiredPermission={3}>
                <ActiveJobs/>
              </ProtectedRoute>
            } />
            <Route path="add-job" element={
              <ProtectedRoute requiredPermission={3}>
                <AddJob/>
              </ProtectedRoute>
            } />
            <Route path=":jobId/final-screening" element={
              <ProtectedRoute requiredPermission={3}>
                <FinalScreeningPage/>
              </ProtectedRoute>
            } />
            <Route path="final-interview" element={
              <ProtectedRoute requiredPermission={3}>
                <FinalInterview/>
              </ProtectedRoute>
            } />
            <Route path="email-templates" element={
              <ProtectedRoute requiredPermission={3}>
                <EmailTemplatesHr/>
              </ProtectedRoute>
            } />
          </Route>
          
          {/* Recruiter Routes */}
          <Route path="recruiter">
            <Route index element={
              <ProtectedRoute requiredPermission={1}>
                <ViewCandidates/>
              </ProtectedRoute>
            } />
            <Route path=":JobId/Initial-Screening" element={
              <ProtectedRoute requiredPermission={1}>
                <InitialScreeningPage/>
              </ProtectedRoute>
            } />
            <Route path="manage-interview" element={
              <ProtectedRoute requiredPermission={1}>
                <ManageInterview/>
              </ProtectedRoute>
            } />
            <Route path="email-templates" element={
              <ProtectedRoute requiredPermission={1}>
                <EmailTemplatesRecruit/>
              </ProtectedRoute>
            } />
          </Route>
        </Route>
      </Routes>
      <Toaster position="top-right" />
    </>
  )
}

export default App