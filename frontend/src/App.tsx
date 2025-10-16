import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from '@/components/ui/toaster'
import { AuthProvider, ProtectedRoute } from '@/lib/auth'
import SignIn from '@/routes/SignIn'
import TeacherDashboard from '@/routes/Teacher/TeacherDashboard'
import StudentDashboard from '@/routes/Student/StudentDashboard'
import { queryClient } from '@/lib/queryClient'
import { useAuth } from '@/lib/auth'
import Register from '@/routes/Register'

function RoleBasedRedirect() {
  const { user, isLoading } = useAuth()
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }
  
  if (!user) {
    return <Navigate to="/signin" replace />
  }
  
  return <Navigate to={`/${user.role}`} replace />
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <Routes>
              <Route path="/signin" element={<SignIn />} />
              <Route path="/register" element={<Register />} />
              <Route 
                path="/teacher" 
                element={
                  <ProtectedRoute role="teacher">
                    <TeacherDashboard />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/student" 
                element={
                  <ProtectedRoute role="student">
                    <StudentDashboard />
                  </ProtectedRoute>
                } 
              />
              <Route path="/" element={<RoleBasedRedirect />} />
              <Route path="*" element={<Navigate to="/signin" replace />} />
            </Routes>
            <Toaster />
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App