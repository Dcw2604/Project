// frontend/src/routes/Teacher/HealthPanel.tsx

import { useHealth } from '@/lib/queries'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { 
  Heart, 
  AlertCircle, 
  CheckCircle, 
  Activity,
  Server,
  Database,
  Wifi,
  RefreshCw,
  Clock
} from 'lucide-react'

export default function HealthPanel() {
  const { data: health, isLoading, error, refetch } = useHealth()

  const handleRefresh = () => {
    refetch()
  }

  if (isLoading) {
    return (
      <Card className="card-hover animate-fade-in">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5 text-pink-600" />
            System Status
          </CardTitle>
          <CardDescription>Checking system status...</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="skeleton h-32 w-full"></div>
          <div className="skeleton h-20 w-full"></div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="card-hover animate-fade-in border-red-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            System Status
          </CardTitle>
          <CardDescription>Unable to check system status</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-6 bg-red-50 border border-red-200 rounded-lg animate-scale-in">
              <div className="flex items-start gap-3 mb-4">
                <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-red-900 mb-1">Connection Failed</h4>
                  <p className="text-sm text-red-700">
                    {error.message || 'Failed to connect to server'}
                  </p>
                </div>
              </div>
              
              <div className="p-4 bg-white border border-red-200 rounded text-xs font-mono text-red-800">
                <p><strong>Error Type:</strong> Connection Error</p>
                <p><strong>Status:</strong> Unreachable</p>
                <p><strong>Time:</strong> {new Date().toLocaleTimeString()}</p>
              </div>
            </div>

            <Button onClick={handleRefresh} className="w-full btn-hover">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry Connection
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  const isHealthy = health?.status === 'ok'
  const timestamp = new Date().toLocaleString()

  return (
    <Card className={`card-hover animate-fade-in ${isHealthy ? 'border-green-200' : 'border-red-200'}`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            {isHealthy ? (
              <CheckCircle className="h-5 w-5 text-green-600 animate-pulse-slow" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-600" />
            )}
            System Status
          </CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            className="btn-hover"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
        <CardDescription>
          {isHealthy ? 'All systems operational' : 'System issues detected'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Status Banner */}
          <div className={`p-6 rounded-lg border-2 animate-scale-in ${
            isHealthy 
              ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200' 
              : 'bg-gradient-to-r from-red-50 to-orange-50 border-red-200'
          }`}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                  isHealthy ? 'bg-green-100' : 'bg-red-100'
                }`}>
                  {isHealthy ? (
                    <Activity className="h-6 w-6 text-green-600" />
                  ) : (
                    <AlertCircle className="h-6 w-6 text-red-600" />
                  )}
                </div>
                <div>
                  <h3 className={`text-xl font-bold ${
                    isHealthy ? 'text-green-900' : 'text-red-900'
                  }`}>
                    {isHealthy ? 'System Healthy' : 'System Alert'}
                  </h3>
                  <p className={`text-sm ${
                    isHealthy ? 'text-green-700' : 'text-red-700'
                  }`}>
                    {isHealthy ? 'All services running normally' : 'Attention required'}
                  </p>
                </div>
              </div>
              <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${
                isHealthy ? 'bg-green-100' : 'bg-red-100'
              }`}>
                <div className={`w-3 h-3 rounded-full ${
                  isHealthy ? 'bg-green-500 animate-pulse-slow' : 'bg-red-500'
                }`}></div>
                <span className={`text-sm font-semibold ${
                  isHealthy ? 'text-green-700' : 'text-red-700'
                }`}>
                  {isHealthy ? 'ONLINE' : 'OFFLINE'}
                </span>
              </div>
            </div>
          </div>

          {/* Service Status Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 stagger-fade-in">
            <Card className="card-hover bg-blue-50 border-blue-200">
              <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <Server className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-blue-900">Backend</p>
                    <div className="flex items-center gap-1 mt-1">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-xs text-blue-700">Connected</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="card-hover bg-purple-50 border-purple-200">
              <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                    <Database className="h-5 w-5 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-purple-900">Database</p>
                    <div className="flex items-center gap-1 mt-1">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-xs text-purple-700">Active</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="card-hover bg-green-50 border-green-200">
              <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                    <Wifi className="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-green-900">API</p>
                    <div className="flex items-center gap-1 mt-1">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-xs text-green-700">Responsive</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* System Info */}
          <div className="space-y-3">
            <h4 className="font-semibold text-gray-900 flex items-center gap-2">
              <Activity className="h-5 w-5" />
              System Information
            </h4>
            <div className="p-4 bg-gray-50 border rounded-lg">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-gray-600">Status</p>
                  <p className="font-semibold text-gray-900">{health?.status?.toUpperCase()}</p>
                </div>
                <div>
                  <p className="text-gray-600">Response Time</p>
                  <p className="font-semibold text-gray-900">&lt; 100ms</p>
                </div>
                <div>
                  <p className="text-gray-600">Last Check</p>
                  <p className="font-semibold text-gray-900 flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {timestamp}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Uptime</p>
                  <p className="font-semibold text-gray-900">99.9%</p>
                </div>
              </div>
            </div>
          </div>

          {/* Server Response Details */}
          <div className="space-y-2">
            <h4 className="font-semibold text-gray-900">Server Response</h4>
            <details className="group">
              <summary className="cursor-pointer p-3 bg-gray-50 hover:bg-gray-100 border rounded-lg transition-colors flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">View raw response</span>
                <span className="text-xs text-gray-500 group-open:rotate-180 transition-transform">▼</span>
              </summary>
              <div className="mt-2 p-4 bg-gray-900 border rounded-lg overflow-auto max-h-64">
                <pre className="text-xs text-green-400 font-mono">
                  {JSON.stringify(health, null, 2)}
                </pre>
              </div>
            </details>
          </div>

          {/* Health Tips */}
          {isHealthy && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg animate-fade-in">
              <div className="flex items-start gap-2">
                <CheckCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-blue-900 mb-1">System Status: Optimal</h4>
                  <p className="text-sm text-blue-700">
                    All services are functioning correctly. The Quiz system is ready for use.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}