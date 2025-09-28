import { useHealth } from '@/lib/queries'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Heart, AlertCircle, CheckCircle } from 'lucide-react'

export default function HealthPanel() {
  const { data: health, isLoading, error } = useHealth()

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5" />
            System Health
          </CardTitle>
          <CardDescription>Checking system status...</CardDescription>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-32 w-full" />
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            System Health
          </CardTitle>
          <CardDescription>Unable to check system status</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">
              Error: {error.message || 'Failed to connect to server'}
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const isHealthy = health?.status === 'ok'

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {isHealthy ? (
            <CheckCircle className="h-5 w-5 text-green-600" />
          ) : (
            <AlertCircle className="h-5 w-5 text-red-600" />
          )}
          System Health
        </CardTitle>
        <CardDescription>
          {isHealthy ? 'All systems operational' : 'System issues detected'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="p-4 bg-gray-50 border rounded-md">
            <h4 className="font-medium mb-2">Server Response</h4>
            <pre className="text-xs text-gray-600 whitespace-pre-wrap">
              {JSON.stringify(health, null, 2)}
            </pre>
          </div>
          
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className={isHealthy ? 'text-green-600' : 'text-red-600'}>
              {isHealthy ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}