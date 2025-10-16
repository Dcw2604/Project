import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { apiClient } from './api'

export type UserRole = 'student' | 'teacher'

export interface User {
  role: UserRole
  name: string
  id?: number
}

interface AuthContextType {
  user: User | null
  login: (username: string, password: string) => Promise<{success: boolean; error?: string}>
  logout: () => Promise<void>
  isLoading: boolean
}
const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      const savedAuth = localStorage.getItem('auth')
      if (savedAuth) {
        try {
          // Verify session with backend
          const result = await apiClient.getCurrentUser()
          if (result.success && result.user) {
            const user: User = {
              id: result.user.id,
              name: result.user.name,
              role: result.user.role as UserRole
            }
            setUser(user)
            localStorage.setItem('auth', JSON.stringify(user))
          } else {
            // Session expired
            localStorage.removeItem('auth')
          }
        } catch {
          localStorage.removeItem('auth')
        }
      }
      setIsLoading(false)
    }
    
    checkAuth()
  }, [])

  const login = async (username: string, password: string) => {
    const result = await apiClient.login(username, password)
    if (result.success && result.user) {
      const user: User = {
        id: result.user.id,
        name: result.user.name,
        role: result.user.role as UserRole
      }
      setUser(user)
      localStorage.setItem('auth', JSON.stringify(user))
      return { success: true }
    }
    return { success: false, error: 'Invalid credentials' }
  }

  const logout = async () => {
    try {
      await apiClient.logout()
    } catch (error) {
      console.error('Logout error:', error)
    }
    setUser(null)
    localStorage.removeItem('auth')
  }

  const value = {
    user,
    login,
    logout,
    isLoading,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

interface ProtectedRouteProps {
  children: ReactNode
  role: UserRole
}


export function ProtectedRoute({ children, role }: ProtectedRouteProps) {
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