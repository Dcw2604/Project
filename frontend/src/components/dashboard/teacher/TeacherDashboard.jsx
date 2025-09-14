import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  Stack,
  Container,
  Paper,
  styled,
  AppBar,
  Toolbar,
  Tab,
  Tabs,
  Badge,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Divider,
} from "@mui/material";
import {
  Dashboard,
  Schedule,
  People,
  Description,
  Assessment,
  Notifications,
  Settings,
  School,
  TrendingUp,
  Assignment,
  CheckCircle,
  Pending,
  Cancel,
  Add,
  MoreVert,
  CalendarMonth,
  Group,
  Book,
  BarChart,
  Quiz,
} from "@mui/icons-material";

// Import teacher components
import ManageStudents from "./ManageStudents";
import ManageSchedule from "./ManageSchedule";
import ManageTests from "./ManageTests";
import ManageExams from "./ManageExams";
import StudentGrades from "./StudentGrades";

const StyledContainer = styled(Container)(({ theme }) => ({
  minHeight: "100vh",
  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
  padding: 0,
  maxWidth: "100% !important",
}));

const GlassCard = styled(Card)(({ theme }) => ({
  background:
    "linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05))",
  backdropFilter: "blur(20px)",
  border: "1px solid rgba(255, 255, 255, 0.2)",
  borderRadius: "20px",
  boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
  color: "white",
  transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
  "&:hover": {
    transform: "translateY(-4px)",
    boxShadow: "0 16px 48px rgba(0, 0, 0, 0.2)",
  },
}));

const StatsCard = styled(GlassCard)(({ theme }) => ({
  height: "140px",
  cursor: "pointer",
}));

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: "16px",
  padding: "12px 24px",
  fontWeight: 600,
  textTransform: "none",
  fontSize: "1rem",
  background:
    "linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1))",
  backdropFilter: "blur(10px)",
  border: "1px solid rgba(255, 255, 255, 0.3)",
  color: "white",
  transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
  "&:hover": {
    background:
      "linear-gradient(135deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.2))",
    transform: "translateY(-2px)",
    boxShadow: "0 8px 25px rgba(0, 0, 0, 0.15)",
  },
}));

const TeacherDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [anchorEl, setAnchorEl] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    totalStudents: 24,
    activeLessons: 8,
    pendingRequests: 3,
    documentsUploaded: 15,
    todayLessons: 5,
    weeklyHours: 28,
    averageRating: 4.8,
    completionRate: 92,
  });

  const [recentActivity, setRecentActivity] = useState([
    {
      id: 1,
      type: "lesson",
      student: "Sarah Johnson",
      subject: "Mathematics",
      time: "10:00 AM",
      status: "completed",
    },
    {
      id: 2,
      type: "request",
      student: "Mike Chen",
      subject: "Physics",
      time: "2:30 PM",
      status: "pending",
    },
    {
      id: 3,
      type: "document",
      name: "Algebra Worksheet.pdf",
      time: "9:15 AM",
      status: "uploaded",
    },
    {
      id: 4,
      type: "lesson",
      student: "Emma Davis",
      subject: "Chemistry",
      time: "3:00 PM",
      status: "scheduled",
    },
  ]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleCreateExamSession = () => {
    setActiveTab(4); // Switch to Exam Sessions tab
  };

  const renderDashboardOverview = () => (
    <Box sx={{ p: 3 }}>
      {/* Welcome Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" fontWeight={800} color="white" mb={1}>
          Welcome back, Professor! 👋
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, color: "white" }}>
          Here's what's happening with your students today
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard>
            <CardContent
              sx={{
                p: 3,
                textAlign: "center",
                height: "100%",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
              }}
            >
              <Group sx={{ fontSize: "2.5rem", color: "#3B82F6", mb: 1 }} />
              <Typography variant="h4" fontWeight={800}>
                {dashboardData.totalStudents}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Total Students
              </Typography>
            </CardContent>
          </StatsCard>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatsCard>
            <CardContent
              sx={{
                p: 3,
                textAlign: "center",
                height: "100%",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
              }}
            >
              <Schedule sx={{ fontSize: "2.5rem", color: "#10B981", mb: 1 }} />
              <Typography variant="h4" fontWeight={800}>
                {dashboardData.todayLessons}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Today's Lessons
              </Typography>
            </CardContent>
          </StatsCard>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatsCard>
            <CardContent
              sx={{
                p: 3,
                textAlign: "center",
                height: "100%",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
              }}
            >
              <Pending sx={{ fontSize: "2.5rem", color: "#F59E0B", mb: 1 }} />
              <Typography variant="h4" fontWeight={800}>
                {dashboardData.pendingRequests}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Pending Requests
              </Typography>
            </CardContent>
          </StatsCard>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatsCard>
            <CardContent
              sx={{
                p: 3,
                textAlign: "center",
                height: "100%",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
              }}
            >
              <Book sx={{ fontSize: "2.5rem", color: "#8B5CF6", mb: 1 }} />
              <Typography variant="h4" fontWeight={800}>
                {dashboardData.documentsUploaded}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Documents
              </Typography>
            </CardContent>
          </StatsCard>
        </Grid>
      </Grid>

      {/* Recent Activity and Quick Actions */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <GlassCard>
            <CardContent sx={{ p: 4 }}>
              <Typography
                variant="h5"
                fontWeight={700}
                mb={3}
                sx={{ display: "flex", alignItems: "center", gap: 1 }}
              >
                <Assessment />
                Recent Activity
              </Typography>

              <Stack spacing={2}>
                {recentActivity.map((activity) => (
                  <Box
                    key={activity.id}
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      bgcolor: "rgba(255, 255, 255, 0.05)",
                    }}
                  >
                    <Stack
                      direction="row"
                      justifyContent="space-between"
                      alignItems="center"
                    >
                      <Box>
                        <Typography variant="body1" fontWeight={600}>
                          {activity.type === "lesson"
                            ? `Lesson with ${activity.student}`
                            : activity.type === "request"
                            ? `New request from ${activity.student}`
                            : `Document: ${activity.name}`}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.7 }}>
                          {activity.type !== "document"
                            ? activity.subject + " • "
                            : ""}
                          {activity.time}
                        </Typography>
                      </Box>
                      <Chip
                        label={activity.status}
                        size="small"
                        sx={{
                          bgcolor:
                            activity.status === "completed"
                              ? "#10B981"
                              : activity.status === "pending"
                              ? "#F59E0B"
                              : activity.status === "scheduled"
                              ? "#3B82F6"
                              : "#8B5CF6",
                          color: "white",
                        }}
                      />
                    </Stack>
                  </Box>
                ))}
              </Stack>
            </CardContent>
          </GlassCard>
        </Grid>

        <Grid item xs={12} md={4}>
          <GlassCard>
            <CardContent sx={{ p: 4 }}>
              <Typography
                variant="h5"
                fontWeight={700}
                mb={3}
                sx={{ display: "flex", alignItems: "center", gap: 1 }}
              >
                <TrendingUp />
                Quick Actions
              </Typography>

              <Stack spacing={2}>
                <ActionButton
                  startIcon={<Quiz />}
                  fullWidth
                  onClick={handleCreateExamSession}
                >
                  Create Exam Session
                </ActionButton>
                <ActionButton startIcon={<Add />} fullWidth>
                  Schedule New Lesson
                </ActionButton>
                <ActionButton startIcon={<People />} fullWidth>
                  View All Students
                </ActionButton>
                <ActionButton startIcon={<Description />} fullWidth>
                  Upload Document
                </ActionButton>
                <ActionButton startIcon={<Assessment />} fullWidth>
                  Generate Report
                </ActionButton>
              </Stack>

              <Divider
                sx={{ my: 3, borderColor: "rgba(255, 255, 255, 0.2)" }}
              />

              <Typography variant="h6" fontWeight={700} mb={2}>
                Performance Metrics
              </Typography>

              <Stack spacing={1}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Weekly Hours</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {dashboardData.weeklyHours}h
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Average Rating</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    ⭐ {dashboardData.averageRating}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Completion Rate</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {dashboardData.completionRate}%
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </GlassCard>
        </Grid>
      </Grid>
    </Box>
  );

  return (
    <StyledContainer>
      {/* App Bar */}
      <AppBar
        position="static"
        sx={{
          bgcolor: "rgba(255, 255, 255, 0.1)",
          backdropFilter: "blur(20px)",
        }}
      >
        <Toolbar>
          <School sx={{ mr: 2, color: "white" }} />
          <Typography
            variant="h6"
            component="div"
            sx={{ flexGrow: 1, color: "white", fontWeight: 700 }}
          >
            Teacher Dashboard
          </Typography>

          <Stack direction="row" spacing={2} alignItems="center">
            <IconButton color="inherit">
              <Badge badgeContent={dashboardData.pendingRequests} color="error">
                <Notifications />
              </Badge>
            </IconButton>

            <IconButton onClick={handleMenuOpen}>
              <Avatar sx={{ bgcolor: "#10B981" }}>T</Avatar>
            </IconButton>

            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              sx={{ mt: 1 }}
            >
              <MenuItem onClick={handleMenuClose}>
                <Settings sx={{ mr: 1 }} /> Settings
              </MenuItem>
              <MenuItem onClick={handleMenuClose}>
                <Dashboard sx={{ mr: 1 }} /> Profile
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleMenuClose}>Logout</MenuItem>
            </Menu>
          </Stack>
        </Toolbar>
      </AppBar>

      {/* Navigation Tabs */}
      <Box
        sx={{
          borderBottom: 1,
          borderColor: "rgba(255, 255, 255, 0.2)",
          bgcolor: "rgba(255, 255, 255, 0.05)",
        }}
      >
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          sx={{
            "& .MuiTab-root": {
              color: "rgba(255, 255, 255, 0.7)",
              fontWeight: 600,
              textTransform: "none",
              fontSize: "1rem",
            },
            "& .Mui-selected": {
              color: "white !important",
            },
            "& .MuiTabs-indicator": {
              backgroundColor: "#10B981",
              height: 3,
              borderRadius: 2,
            },
          }}
        >
          <Tab icon={<Dashboard />} label="Overview" />
          <Tab icon={<People />} label="Students" />
          <Tab icon={<CalendarMonth />} label="Schedule" />
          <Tab icon={<Assignment />} label="Tests" />
          <Tab icon={<Quiz />} label="Exam Sessions" />
          <Tab icon={<Assessment />} label="Student Grades" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      <Box>
        {activeTab === 0 && renderDashboardOverview()}
        {activeTab === 1 && <ManageStudents />}
        {activeTab === 2 && <ManageSchedule />}
        {activeTab === 3 && <ManageTests />}
        {activeTab === 4 && (
          <Box>
            <ManageExams />
          </Box>
        )}
        {activeTab === 5 && <StudentGrades />}
      </Box>
    </StyledContainer>
  );
};

export default TeacherDashboard;
