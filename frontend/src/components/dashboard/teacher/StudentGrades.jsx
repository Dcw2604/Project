import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  TextField,
  InputAdornment,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Avatar,
  Tooltip,
  LinearProgress,
} from "@mui/material";
import GradesAnalytics from "./GradesAnalytics";
import {
  Search,
  FilterList,
  Download,
  Visibility,
  Assessment,
  TrendingUp,
  TrendingDown,
  School,
  Person,
  Grade,
  Analytics,
  Refresh,
} from "@mui/icons-material";

const StudentGrades = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [gradesData, setGradesData] = useState(null);
  const [filteredStudents, setFilteredStudents] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [filterDifficulty, setFilterDifficulty] = useState("all");
  const [sortBy, setSortBy] = useState("percentage");
  const [viewMode, setViewMode] = useState(0); // 0: Table, 1: Analytics

  // Load grades data
  useEffect(() => {
    loadGradesData();
  }, []);

  // Filter students based on search and filters
  useEffect(() => {
    if (!gradesData) return;

    let filtered = gradesData.individual_insights || [];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(
        (student) =>
          student.student_name
            .toLowerCase()
            .includes(searchTerm.toLowerCase()) ||
          student.exam_title.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Difficulty filter
    if (filterDifficulty !== "all") {
      filtered = filtered.filter(
        (student) =>
          student.performance_summary.difficulty_reached === filterDifficulty
      );
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case "percentage":
          return (
            b.performance_summary.percentage - a.performance_summary.percentage
          );
        case "name":
          return a.student_name.localeCompare(b.student_name);
        case "date":
          return new Date(b.completion_date) - new Date(a.completion_date);
        default:
          return 0;
      }
    });

    setFilteredStudents(filtered);
  }, [gradesData, searchTerm, filterDifficulty, sortBy]);

  const loadGradesData = async () => {
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
        setGradesData(data);
      } else {
        const errorData = await response.json();
        setError(errorData.error || "שגיאה בטעינת נתוני הציונים");
      }
    } catch (err) {
      setError("שגיאת רשת. אנא נסה שנית.");
      console.error("Error loading grades data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (student) => {
    setSelectedStudent(student);
    setDetailDialogOpen(true);
  };

  const handleCloseDetails = () => {
    setDetailDialogOpen(false);
    setSelectedStudent(null);
  };

  const getGradeColor = (percentage) => {
    if (percentage >= 90) return "success";
    if (percentage >= 75) return "primary";
    if (percentage >= 60) return "warning";
    return "error";
  };

  const getGradeLabel = (percentage) => {
    if (percentage >= 90) return "מעולה";
    if (percentage >= 75) return "טוב מאוד";
    if (percentage >= 60) return "טוב";
    return "צריך שיפור";
  };

  const getDifficultyLabel = (difficulty) => {
    const labels = {
      easy: "קל",
      medium: "בינוני",
      hard: "קשה",
    };
    return labels[difficulty] || difficulty;
  };

  const renderOverview = () => {
    if (!gradesData) return null;

    const summary = gradesData.summary || {};
    const distribution = summary.performance_distribution || {};

    return (
      <Grid container spacing={3} sx={{ mb: 4 }}>
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
                <Typography variant="h6">מעולה (90%+)</Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: "bold" }}>
                {distribution.excellent || 0}
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
                <Grade sx={{ mr: 1 }} />
                <Typography variant="h6">צריך שיפור</Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: "bold" }}>
                {distribution.needs_improvement || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderStudentsTable = () => {
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

    if (filteredStudents.length === 0) {
      return (
        <Alert severity="info" sx={{ mb: 2 }}>
          לא נמצאו תלמידים עם הקריטריונים שנבחרו
        </Alert>
      );
    }

    return (
      <TableContainer
        component={Paper}
        sx={{ borderRadius: 2, overflow: "hidden" }}
      >
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: "#f5f5f5" }}>
              <TableCell sx={{ fontWeight: "bold" }}>תלמיד</TableCell>
              <TableCell sx={{ fontWeight: "bold" }}>מבחן</TableCell>
              <TableCell sx={{ fontWeight: "bold" }}>ציון</TableCell>
              <TableCell sx={{ fontWeight: "bold" }}>אחוזים</TableCell>
              <TableCell sx={{ fontWeight: "bold" }}>רמת קושי</TableCell>
              <TableCell sx={{ fontWeight: "bold" }}>תאריך</TableCell>
              <TableCell sx={{ fontWeight: "bold" }}>פעולות</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredStudents.map((student, index) => (
              <TableRow key={index} hover>
                <TableCell>
                  <Box sx={{ display: "flex", alignItems: "center" }}>
                    <Avatar sx={{ mr: 2, bgcolor: "primary.main" }}>
                      {student.student_name.charAt(0)}
                    </Avatar>
                    <Typography variant="body1" sx={{ fontWeight: 500 }}>
                      {student.student_name}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {student.exam_title}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                    {student.performance_summary.score}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box sx={{ display: "flex", alignItems: "center" }}>
                    <Chip
                      label={student.performance_summary.percentage + "%"}
                      color={getGradeColor(
                        student.performance_summary.percentage
                      )}
                      size="small"
                      sx={{ mr: 1 }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      {getGradeLabel(student.performance_summary.percentage)}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={getDifficultyLabel(
                      student.performance_summary.difficulty_reached
                    )}
                    color="info"
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {new Date(student.completion_date).toLocaleDateString(
                      "he-IL"
                    )}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Tooltip title="צפה בפרטים">
                    <IconButton
                      onClick={() => handleViewDetails(student)}
                      color="primary"
                      size="small"
                    >
                      <Visibility />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  const renderStudentDetails = () => {
    if (!selectedStudent) return null;

    return (
      <Dialog
        open={detailDialogOpen}
        onClose={handleCloseDetails}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Person sx={{ mr: 1 }} />
            פרטי תלמיד: {selectedStudent.student_name}
          </Box>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  ביצועים כללים
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    ציון: {selectedStudent.performance_summary.score}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    אחוזים: {selectedStudent.performance_summary.percentage}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    רמת שליטה:{" "}
                    {selectedStudent.performance_summary.mastery_level}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    רמת קושי הגעה:{" "}
                    {getDifficultyLabel(
                      selectedStudent.performance_summary.difficulty_reached
                    )}
                  </Typography>
                </Box>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  נקודות חוזק
                </Typography>
                {selectedStudent.strengths.map((strength, index) => (
                  <Chip
                    key={index}
                    label={strength}
                    color="success"
                    size="small"
                    sx={{ mr: 1, mb: 1 }}
                  />
                ))}
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  תחומים לשיפור
                </Typography>
                {selectedStudent.weaknesses.map((weakness, index) => (
                  <Chip
                    key={index}
                    label={weakness}
                    color="warning"
                    size="small"
                    sx={{ mr: 1, mb: 1 }}
                  />
                ))}
              </Card>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetails} color="primary">
            סגור
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

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
          ציוני תלמידים
        </Typography>
        <Box sx={{ display: "flex", gap: 2 }}>
          <Button
            variant={viewMode === 0 ? "contained" : "outlined"}
            onClick={() => setViewMode(0)}
            startIcon={<Assessment />}
          >
            טבלת ציונים
          </Button>
          <Button
            variant={viewMode === 1 ? "contained" : "outlined"}
            onClick={() => setViewMode(1)}
            startIcon={<Analytics />}
          >
            ניתוח מתקדם
          </Button>
          <Button
            variant="contained"
            startIcon={<Refresh />}
            onClick={loadGradesData}
            disabled={loading}
          >
            רענן נתונים
          </Button>
        </Box>
      </Box>

      {/* Content based on view mode */}
      {viewMode === 0 ? (
        <>
          {/* Overview Cards */}
          {renderOverview()}

          {/* Filters and Search */}
          <Card sx={{ mb: 3, p: 2 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  placeholder="חיפוש תלמיד או מבחן..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>רמת קושי</InputLabel>
                  <Select
                    value={filterDifficulty}
                    onChange={(e) => setFilterDifficulty(e.target.value)}
                    label="רמת קושי"
                  >
                    <MenuItem value="all">הכל</MenuItem>
                    <MenuItem value="easy">קל</MenuItem>
                    <MenuItem value="medium">בינוני</MenuItem>
                    <MenuItem value="hard">קשה</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>מיון לפי</InputLabel>
                  <Select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    label="מיון לפי"
                  >
                    <MenuItem value="percentage">אחוזים</MenuItem>
                    <MenuItem value="name">שם תלמיד</MenuItem>
                    <MenuItem value="date">תאריך</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={2}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Download />}
                  disabled={!gradesData}
                >
                  ייצא נתונים
                </Button>
              </Grid>
            </Grid>
          </Card>

          {/* Students Table */}
          {renderStudentsTable()}
        </>
      ) : (
        <GradesAnalytics />
      )}

      {/* Student Details Dialog */}
      {renderStudentDetails()}
    </Box>
  );
};

export default StudentGrades;
