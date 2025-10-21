// frontend/src/routes/SignIn.tsx

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/hooks/use-toast'
import { LogIn, User, Lock, GraduationCap, AlertCircle } from 'lucide-react'

export default function SignIn() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState<{ username?: string; password?: string }>({})
  const { login } = useAuth()
  const navigate = useNavigate()
  const { toast } = useToast()

  const validateForm = () => {
    const newErrors: { username?: string; password?: string } = {}
    
    if (!username.trim()) {
      newErrors.username = 'Username is required'
    }
    
    if (!password.trim()) {
      newErrors.password = 'Password is required'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setIsLoading(true)
    
    try {
      const result = await login(username.trim(), password.trim())
      
      if (result.success) {
        toast({
          title: "Welcome back! 👋",
          description: "Signed in successfully",
        })
        
        window.location.href = '/'
      } else {
        toast({
          title: "Sign In Failed",
          description: result.error || "Invalid username or password",
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to sign in. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md animate-scale-in">
        {/* Logo/Brand */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 gradient-blue rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg animate-pulse-slow">
            <GraduationCap className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gradient mb-2">Exam System</h1>
          <p className="text-gray-600">Sign in to continue</p>
        </div>

        <Card className="card-hover shadow-xl border-0">
          <CardHeader className="space-y-1 pb-6">
            <CardTitle className="text-2xl font-bold text-center flex items-center justify-center gap-2">
              <LogIn className="h-6 w-6 text-blue-600" />
              Sign In
            </CardTitle>
            <CardDescription className="text-center">
              Enter your credentials to access your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Username */}
              <div className="space-y-2">
                <Label htmlFor="username" className="text-sm font-medium">
                  Username
                </Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    id="username"
                    type="text"
                    placeholder="Enter your username"
                    value={username}
                    onChange={(e) => {
                      setUsername(e.target.value)
                      if (errors.username) setErrors({ ...errors, username: undefined })
                    }}
                    className={`pl-10 ${errors.username ? 'border-red-500' : ''}`}
                    autoComplete="username"
                  />
                </div>
                {errors.username && (
                  <p className="text-xs text-red-600 flex items-center gap-1 animate-fade-in">
                    <AlertCircle className="h-3 w-3" />
                    {errors.username}
                  </p>
                )}
              </div>
              
              {/* Password */}
              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium">
                  Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value)
                      if (errors.password) setErrors({ ...errors, password: undefined })
                    }}
                    className={`pl-10 ${errors.password ? 'border-red-500' : ''}`}
                    autoComplete="current-password"
                  />
                </div>
                {errors.password && (
                  <p className="text-xs text-red-600 flex items-center gap-1 animate-fade-in">
                    <AlertCircle className="h-3 w-3" />
                    {errors.password}
                  </p>
                )}
              </div>
              
              {/* Submit Button */}
              <Button 
                type="submit" 
                className="w-full btn-hover gradient-blue text-white shadow-lg h-11"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <div className="spinner w-5 h-5 border-2 mr-2"></div>
                    Signing in...
                  </>
                ) : (
                  <>
                    <LogIn className="h-5 w-5 mr-2" />
                    Sign In
                  </>
                )}
              </Button>
              
              {/* Register Link */}
              <div className="text-center pt-4 border-t">
                <p className="text-sm text-gray-600">
                  Don't have an account?{' '}
                  <a 
                    href="/register" 
                    className="text-blue-600 hover:text-blue-700 font-semibold hover:underline transition-colors"
                  >
                    Register now
                  </a>
                </p>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Footer */}
        <p className="text-center text-sm text-gray-500 mt-6">
          © 2025 Exam System. All rights reserved.
        </p>
      </div>
    </div>
  )
}