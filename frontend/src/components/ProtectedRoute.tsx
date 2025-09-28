import { Navigate } from 'react-router-dom'
import { useAuth, UserRole } from '@/lib/auth'

interface ProtectedRouteProps {
  children: React.ReactNode
  role: UserRole
}

export default function ProtectedRoute({ children, role }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!user || user.role !== role) {
    return <Navigate to="/signin" replace />
  }

  return <>{children}</>
}
