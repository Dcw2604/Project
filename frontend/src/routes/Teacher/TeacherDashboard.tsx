// frontend/src/routes/Teacher/TeacherDashboard.tsx

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { 
  LogOut, 
  Upload, 
  Plus, 
  Heart, 
  BarChart3, 
  FileText, 
  Home,
  BookOpen,
  Users,
  TrendingUp,
  Clock,
  CheckCircle2,
  AlertCircle,
  Activity
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import UploadDocument from "./UploadDocument";
import CreateExam from "./CreateExam";
import HealthPanel from "./HealthPanel";
import ExamResults from "./ExamResults";
import ViewQuestions from "./ViewQuestions";

interface DashboardStats {
  totalExams: number;
  totalStudents: number;
  completionRate: number;
  activeExams: number;
}

interface RecentActivity {
  id: string;
  type: 'exam_created' | 'exam_completed' | 'document_uploaded';
  message: string;
  time: string;
  icon: any;
  color: string;
}

interface RecentActivity {
  id: string;
  type: 'exam_created' | 'exam_completed' | 'document_uploaded';
  message: string;
  time: string;
  icon: any;
  color: string;
}

interface RecentActivity {
  id: string;
  type: 'exam_created' | 'exam_completed' | 'document_uploaded';
  message: string;
  time: string;
  icon: any;
  color: string;
}

interface Exam {
  id: number;
  title: string;
  document_title: string;
  total_questions: number;
  created_at: string;
}

export default function TeacherDashboard() {
  const { user, logout } = useAuth();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState("overview");
  const [stats, setStats] = useState<DashboardStats>({
    totalExams: 0,
    totalStudents: 0,
    completionRate: 0,
    activeExams: 0
  });
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [isLoadingStats, setIsLoadingStats] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
    fetchRecentActivity();
  }, []);

  const fetchDashboardStats = async () => {
    setIsLoadingStats(true);
    try {
      // Fetch exams
      const examsResponse = await fetch('http://127.0.0.1:8000/api/exams/');
      let totalExams = 0;
      let examsData: { success: boolean; exams: Exam[] } = { success: false, exams: [] };
      
      if (examsResponse.ok) {
        const contentType = examsResponse.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
          examsData = await examsResponse.json();
          totalExams = examsData.success ? examsData.exams.length : 0;
        }
      }
      
  
      // Calculate stats from exam results
      let totalStudentsSeen = new Set();
      let totalCompletions = 0;
      let totalAttempts = 0;
  
      if (examsData.success) {
        for (const exam of examsData.exams) {
          try {
            const resultsResponse = await fetch(`http://127.0.0.1:8000/api/exams/${exam.id}/results/`);
            if (resultsResponse.ok) {
              const contentType = resultsResponse.headers.get("content-type");
              if (contentType && contentType.includes("application/json")) {
                const resultsData = await resultsResponse.json();
                
                if (resultsData.success && resultsData.results) {
                  resultsData.results.forEach((result: any) => {
                    totalStudentsSeen.add(result.student_id);
                    totalAttempts++;
                    if (result.completed_at) {
                      totalCompletions++;
                    }
                  });
                }
              }
            }
          } catch (err) {
            console.log('Could not fetch results for exam', exam.id);
          }
        }
      }
  
      const completionRate = totalAttempts > 0 
        ? Math.round((totalCompletions / totalAttempts) * 100) 
        : 0;

    setStats({
      totalExams,
      totalStudents: totalStudentsSeen.size,
      completionRate,
      activeExams: totalExams
    });    
  
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
      toast({
        title: "Warning",
        description: "Some dashboard stats could not be loaded",
        variant: "destructive",
      });
    } finally {
      setIsLoadingStats(false);
    }
  };

  const fetchRecentActivity = async () => {
    // Simulate recent activity - you can implement real API calls
    const mockActivity: RecentActivity[] = [
      {
        id: '1',
        type: 'exam_completed',
        message: 'Student completed "Math Final Exam"',
        time: '2 hours ago',
        icon: CheckCircle2,
        color: 'text-green-600'
      },
      {
        id: '2',
        type: 'exam_created',
        message: 'New exam "Physics Quiz" created',
        time: '5 hours ago',
        icon: Plus,
        color: 'text-blue-600'
      },
      {
        id: '3',
        type: 'document_uploaded',
        message: 'Document "Chapter 5 Notes" uploaded',
        time: '1 day ago',
        icon: Upload,
        color: 'text-purple-600'
      }
    ];
    //setRecentActivity(mockActivity);
    setRecentActivity([]);
  };

  const handleLogout = () => {
    logout();
    toast({
      title: "Signed Out",
      description: "You have been signed out successfully",
    });
  };

  const handleQuickAction = (tab: string) => {
    setActiveTab(tab);
    toast({
      title: "Navigation",
      description: `Switched to ${tab} section`,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Enhanced Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <BookOpen className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Teacher Dashboard
                </h1>
                <p className="text-sm text-gray-500">
                  Welcome back, {user?.name}
                </p>
              </div>
            </div>
            <Button 
              variant="outline" 
              onClick={handleLogout}
              className="hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-colors"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="space-y-6"
        >
          <TabsList className="grid w-full grid-cols-6 bg-white shadow-sm p-1">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <Home className="h-4 w-4" />
              <span className="hidden sm:inline">Overview</span>
            </TabsTrigger>
            <TabsTrigger value="upload" className="flex items-center gap-2">
              <Upload className="h-4 w-4" />
              <span className="hidden sm:inline">Upload</span>
            </TabsTrigger>
            <TabsTrigger value="create" className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              <span className="hidden sm:inline">Create</span>
            </TabsTrigger>
            <TabsTrigger value="questions" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              <span className="hidden sm:inline">Questions</span>
            </TabsTrigger>
            <TabsTrigger value="health" className="flex items-center gap-2">
              <Heart className="h-4 w-4" />
              <span className="hidden sm:inline">Health</span>
            </TabsTrigger>
            <TabsTrigger value="results" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              <span className="hidden sm:inline">Results</span>
            </TabsTrigger>
          </TabsList>

          {/* NEW: Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <Card className="border-l-4 border-l-blue-500 hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Total Exams</p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">
                        {isLoadingStats ? "..." : stats.totalExams}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {stats.activeExams} active
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <BarChart3 className="h-6 w-6 text-blue-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-l-4 border-l-green-500 hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Total Students</p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">
                        {isLoadingStats ? "..." : stats.totalStudents}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Unique students
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                      <Users className="h-6 w-6 text-green-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>


              <Card className="border-l-4 border-l-orange-500 hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Completion Rate</p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">
                        {isLoadingStats ? "..." : `${stats.completionRate}%`}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Exam completion
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                      <TrendingUp className="h-6 w-6 text-orange-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions & Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Quick Actions */}
              <Card className="lg:col-span-1">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    Quick Actions
                  </CardTitle>
                  <CardDescription>Common tasks and shortcuts</CardDescription>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Button 
                    onClick={() => handleQuickAction('upload')} 
                    className="w-full justify-start"
                    variant="outline"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Document
                  </Button>
                  <Button 
                    onClick={() => handleQuickAction('create')} 
                    className="w-full justify-start"
                    variant="outline"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Create New Exam
                  </Button>
                  <Button 
                    onClick={() => handleQuickAction('results')} 
                    className="w-full justify-start"
                    variant="outline"
                  >
                    <BarChart3 className="h-4 w-4 mr-2" />
                    View Results
                  </Button>
                  <Button 
                    onClick={() => handleQuickAction('questions')} 
                    className="w-full justify-start"
                    variant="outline"
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    View Questions
                  </Button>
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="h-5 w-5" />
                    Recent Activity
                  </CardTitle>
                  <CardDescription>Latest updates and actions</CardDescription>
                </CardHeader>
                <CardContent>
                  {recentActivity.length > 0 ? (
                    <div className="space-y-4">
                      {recentActivity.map((activity) => {
                        const Icon = activity.icon;
                        return (
                          <div 
                            key={activity.id} 
                            className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                          >
                            <div className={`w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0`}>
                              <Icon className={`h-5 w-5 ${activity.color}`} />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900">
                                {activity.message}
                              </p>
                              <p className="text-xs text-gray-500 mt-1">
                                {activity.time}
                              </p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <Activity className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                      <p>No recent activity</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* System Status */}
            <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <div>
                      <p className="font-semibold text-gray-900">System Status: Operational</p>
                      <p className="text-sm text-gray-600">All services running normally</p>
                    </div>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleQuickAction('health')}
                  >
                    <Heart className="h-4 w-4 mr-2" />
                    View Health Panel
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="upload">
            <UploadDocument />
          </TabsContent>

          <TabsContent value="create">
            <CreateExam />
          </TabsContent>

          <TabsContent value="questions">
            <ViewQuestions />
          </TabsContent>

          <TabsContent value="health">
            <HealthPanel />
          </TabsContent>

          <TabsContent value="results">
            <ExamResults />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}