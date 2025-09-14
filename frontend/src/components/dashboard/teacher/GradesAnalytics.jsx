import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Paper,
  CircularProgress,
  Alert,
  Button,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress,
  Divider,
} from "@mui/material";
import {
  Analytics,
  TrendingUp,
  TrendingDown,
  School,
  Assessment,
  Psychology,
  Refresh,
  BarChart,
  PieChart,
  Timeline,
} from "@mui/icons-material";
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from "recharts";

const GradesAnalytics = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [analyticsData, setAnalyticsData] = useState(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const loadAnalyticsData = async () => {
    setLoading(true);
    setError("");

    try {
      const token = localStorage.getItem("authToken");
      const response = await fetch(
        "http://127.0.0.1:8000/api/exam/teacher-dashboard/",
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Token ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAnalyticsData(data);
      } else {
        const errorData = await response.json();
        setError(errorData.error || "שגיאה בטעינת נתוני הניתוח");
      }
    } catch (err) {
      setError("שגיאת רשת. אנא נסה שנית.");
      console.error("Error loading analytics data:", err);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyLabel = (difficulty) => {
    const labels = {
      easy: "קל",
      medium: "בינוני",
      hard: "קשה",
    };
    return labels[difficulty] || difficulty;
  };

  const getGradeColor = (percentage) => {
    if (percentage >= 90) return "#4caf50";
    if (percentage >= 75) return "#2196f3";
    if (percentage >= 60) return "#ff9800";
    return "#f44336";
  };

  const renderOverview = () => {
    if (!analyticsData) return null;

    const summary = analyticsData.summary || {};
    const distribution = summary.performance_distribution || {};

    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Card
            sx={{
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "white",
            }}
          >
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <School sx={{ mr: 1 }} />
                <Typography variant="h6">סה"כ תלמידים</Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: "bold" }}>
                {summary.total_students || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card
            sx={{
              background: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
              color: "white",
            }}
          >
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <Assessment sx={{ mr: 1 }} />
                <Typography variant="h6">ציון ממוצע</Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: "bold" }}>
                {summary.average_score || 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card
            sx={{
              background: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
              color: "white",
            }}
          >
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <TrendingUp sx={{ mr: 1 }} />
                <Typography variant="h6">שיעור הצלחה</Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: "bold" }}>
                {Math.round(
                  ((distribution.excellent +
                    distribution.good +
                    distribution.satisfactory) /
                    summary.total_students) *
                    100
                ) || 0}
                %
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card
            sx={{
              background: "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
              color: "white",
            }}
          >
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <Psychology sx={{ mr: 1 }} />
                <Typography variant="h6">מבחנים פעילים</Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: "bold" }}>
                {summary.total_exams || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderPerformanceDistribution = () => {
    if (!analyticsData) return null;

    const distribution = analyticsData.summary?.performance_distribution || {};
    const total = Object.values(distribution).reduce(
      (sum, count) => sum + count,
      0
    );

    const data = [
      {
        name: "מעולה (90%+)",
        value: distribution.excellent || 0,
        color: "#4caf50",
      },
      {
        name: "טוב מאוד (75-89%)",
        value: distribution.good || 0,
        color: "#2196f3",
      },
      {
        name: "טוב (60-74%)",
        value: distribution.satisfactory || 0,
        color: "#ff9800",
      },
      {
        name: "צריך שיפור (<60%)",
        value: distribution.needs_improvement || 0,
        color: "#f44336",
      },
    ];

    return (
      <Card sx={{ p: 3 }}>
        <Typography
          variant="h6"
          gutterBottom
          sx={{ display: "flex", alignItems: "center" }}
        >
          <PieChart sx={{ mr: 1 }} />
          התפלגות ביצועים
        </Typography>
        <Box sx={{ height: 400 }}>
          <ResponsiveContainer width="100%" height="100%">
            <RechartsPieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name}: ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </RechartsPieChart>
          </ResponsiveContainer>
        </Box>
      </Card>
    );
  };

  const renderDifficultyAnalysis = () => {
    if (!analyticsData?.difficulty_analysis) return null;

    const difficultyData = Object.entries(
      analyticsData.difficulty_analysis
    ).map(([level, stats]) => ({
      level: getDifficultyLabel(level),
      accuracy: stats.average_accuracy,
      students: stats.students_attempted,
      color: getGradeColor(stats.average_accuracy),
    }));

    return (
      <Card sx={{ p: 3 }}>
        <Typography
          variant="h6"
          gutterBottom
          sx={{ display: "flex", alignItems: "center" }}
        >
          <BarChart sx={{ mr: 1 }} />
          ניתוח לפי רמות קושי
        </Typography>
        <Box sx={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <RechartsBarChart data={difficultyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="level" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="accuracy" fill="#8884d8" />
            </RechartsBarChart>
          </ResponsiveContainer>
        </Box>
      </Card>
    );
  };

  const renderCommonMistakes = () => {
    if (!analyticsData?.common_mistakes) return null;

    return (
      <Card sx={{ p: 3 }}>
        <Typography
          variant="h6"
          gutterBottom
          sx={{ display: "flex", alignItems: "center" }}
        >
          <TrendingDown sx={{ mr: 1 }} />
          שאלות קשות ביותר
        </Typography>
        <List>
          {analyticsData.common_mistakes.slice(0, 5).map((mistake, index) => (
            <ListItem key={index}>
              <ListItemIcon>
                <Chip
                  label={`${mistake.accuracy}%`}
                  color={
                    mistake.accuracy < 50
                      ? "error"
                      : mistake.accuracy < 70
                      ? "warning"
                      : "success"
                  }
                  size="small"
                />
              </ListItemIcon>
              <ListItemText
                primary={mistake.question_text}
                secondary={`רמת קושי: ${getDifficultyLabel(
                  mistake.difficulty
                )} | ${mistake.total_attempts} ניסיונות`}
              />
            </ListItem>
          ))}
        </List>
      </Card>
    );
  };

  const renderIndividualInsights = () => {
    if (!analyticsData?.individual_insights) return null;

    return (
      <Card sx={{ p: 3 }}>
        <Typography
          variant="h6"
          gutterBottom
          sx={{ display: "flex", alignItems: "center" }}
        >
          <Psychology sx={{ mr: 1 }} />
          תובנות אישיות
        </Typography>
        <Grid container spacing={2}>
          {analyticsData.individual_insights
            .slice(0, 6)
            .map((student, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Paper sx={{ p: 2, border: "1px solid #e0e0e0" }}>
                  <Typography
                    variant="subtitle1"
                    sx={{ fontWeight: "bold", mb: 1 }}
                  >
                    {student.student_name}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 1 }}
                  >
                    {student.exam_title}
                  </Typography>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                    <Typography variant="body2" sx={{ mr: 1 }}>
                      ציון: {student.performance_summary.score}
                    </Typography>
                    <Chip
                      label={`${student.performance_summary.percentage}%`}
                      color={
                        getGradeColor(
                          student.performance_summary.percentage
                        ) === "#4caf50"
                          ? "success"
                          : getGradeColor(
                              student.performance_summary.percentage
                            ) === "#2196f3"
                          ? "primary"
                          : getGradeColor(
                              student.performance_summary.percentage
                            ) === "#ff9800"
                          ? "warning"
                          : "error"
                      }
                      size="small"
                    />
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={student.performance_summary.percentage}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Paper>
              </Grid>
            ))}
        </Grid>
      </Card>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Typography variant="h4" sx={{ fontWeight: "bold", color: "#333" }}>
          ניתוח מתקדם של ציונים
        </Typography>
        <Button
          variant="contained"
          startIcon={<Refresh />}
          onClick={loadAnalyticsData}
          disabled={loading}
        >
          רענן נתונים
        </Button>
      </Box>

      {/* Overview Cards */}
      {renderOverview()}

      {/* Tabs for different analytics views */}
      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
        >
          <Tab label="התפלגות ביצועים" />
          <Tab label="ניתוח קושי" />
          <Tab label="שגיאות נפוצות" />
          <Tab label="תובנות אישיות" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && renderPerformanceDistribution()}
      {activeTab === 1 && renderDifficultyAnalysis()}
      {activeTab === 2 && renderCommonMistakes()}
      {activeTab === 3 && renderIndividualInsights()}
    </Box>
  );
};

export default GradesAnalytics;
