import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Chip,
  Stack,
  Paper,
  Divider,
  styled,
  Alert,
  Snackbar,
  CircularProgress,
  Tooltip,
  Menu,
  MenuItem,
  Fab,
  Tab,
  Tabs,
} from "@mui/material";
import {
  Add,
  Edit,
  Delete,
  MoreVert,
  Quiz,
  Timer,
  School,
  Visibility,
  Assignment,
  People,
  CheckCircle,
  Schedule,
  FilterList,
} from "@mui/icons-material";
import CreateExamSession from "./CreateExamSession";
import api from "../../../services/api";

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

const StyledButton = styled(Button)(({ theme }) => ({
  borderRadius: "12px",
  padding: "8px 16px",
  fontWeight: 600,
  textTransform: "none",
  background:
    "linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1))",
  backdropFilter: "blur(10px)",
  border: "1px solid rgba(255, 255, 255, 0.3)",
  color: "white",
  "&:hover": {
    background:
      "linear-gradient(135deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.2))",
  },
}));

const ExamCard = styled(GlassCard)(({ theme }) => ({
  marginBottom: "1rem",
  cursor: "pointer",
  position: "relative",
}));

const ManageExams = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [selectedExam, setSelectedExam] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);

  // New states for exam details
  const [examDetails, setExamDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  useEffect(() => {
    if (activeTab === 1) {
      // Only load when on "Manage" tab
      loadExams();
    }
  }, [activeTab]);

  const loadExams = async () => {
    setLoading(true);
    try {
      const data = await api.examSessions.list();
      console.log("📊 Exam sessions response:", data);
      // The API returns { exam_sessions: [...], total_count: N }
      setExams(data.exam_sessions || []);
    } catch (error) {
      console.error("Error loading exam sessions:", error);
      setError("Failed to load exam sessions. Please try again.");
      setExams([]);
    } finally {
      setLoading(false);
    }
  };

  // New function to load exam details
  const loadExamDetails = async (examId) => {
    try {
      setLoadingDetails(true);
      const response = await fetch(
        `http://127.0.0.1:8000/api/exam-sessions/${examId}/details/`,
        {
          headers: {
            Authorization: `Token ${localStorage.getItem("authToken")}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        console.log("📊 Exam details loaded:", data);
        setExamDetails(data);
      } else {
        throw new Error("Failed to load exam details");
      }
    } catch (error) {
      console.error("Error loading exam details:", error);
      setError("Failed to load exam details");
    } finally {
      setLoadingDetails(false);
    }
  };

  const handleDeleteExam = async (examId) => {
    try {
      await api.examSessions.delete(examId);
      setSuccess("Exam session deleted successfully");
      loadExams();
    } catch (error) {
      console.error("Error deleting exam session:", error);
      setError("Failed to delete exam session. Please try again.");
    }
    setDeleteDialogOpen(false);
    setSelectedExam(null); // Clear selectedExam after operation
  };

  const handleMenuClick = (event, exam) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedExam(exam);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedExam(null);
  };

  const handleMenuCloseOnly = () => {
    setAnchorEl(null);
  };

  const handleViewExam = (exam) => {
    setSelectedExam(exam);
    setViewDialogOpen(true);
    loadExamDetails(exam.id);
    handleMenuClose();
  };

  const handleEditExam = () => {
    setEditDialogOpen(true);
    handleMenuClose();
  };

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true);
    handleMenuCloseOnly(); // Only close menu, keep selectedExam
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "draft":
        return "warning";
      case "published":
        return "success";
      case "archived":
        return "default";
      default:
        return "primary";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "draft":
        return <Schedule />;
      case "published":
        return <CheckCircle />;
      case "archived":
        return <Assignment />;
      default:
        return <Quiz />;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const handleExamCreated = () => {
    setSuccess("Exam created successfully!");
    if (activeTab === 1) {
      loadExams(); // Refresh the list if we're on the manage tab
    }
  };

  const renderCreateTab = () => (
    <Box>
      <CreateExamSession onSuccess={handleExamCreated} />
    </Box>
  );

  const renderManageTab = () => (
    <Box>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Typography variant="h5" sx={{ color: "white", fontWeight: 600 }}>
          Manage Exams
        </Typography>
        <StyledButton startIcon={<Add />} onClick={() => setActiveTab(0)}>
          Create New Exam
        </StyledButton>
      </Box>

      {loading ? (
        <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
          <CircularProgress sx={{ color: "white" }} />
        </Box>
      ) : exams.length === 0 ? (
        <GlassCard>
          <CardContent sx={{ textAlign: "center", p: 4 }}>
            <Quiz
              sx={{ fontSize: "4rem", color: "rgba(255,255,255,0.5)", mb: 2 }}
            />
            <Typography
              variant="h6"
              sx={{ color: "rgba(255,255,255,0.8)", mb: 2 }}
            >
              No Exams Created Yet
            </Typography>
            <Typography
              variant="body1"
              sx={{ color: "rgba(255,255,255,0.6)", mb: 3 }}
            >
              Start by creating your first exam to assess your students.
            </Typography>
            <StyledButton startIcon={<Add />} onClick={() => setActiveTab(0)}>
              Create First Exam
            </StyledButton>
          </CardContent>
        </GlassCard>
      ) : (
        <Grid container spacing={3}>
          {exams.map((exam) => (
            <Grid item xs={12} md={6} lg={4} key={exam.id}>
              <ExamCard onClick={() => handleViewExam(exam)}>
                <CardContent>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                      mb: 2,
                    }}
                  >
                    <Typography
                      variant="h6"
                      sx={{ color: "white", fontWeight: 600, flexGrow: 1 }}
                    >
                      {exam.title}
                    </Typography>
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuClick(e, exam)}
                      sx={{ color: "rgba(255,255,255,0.7)" }}
                    >
                      <MoreVert />
                    </IconButton>
                  </Box>

                  <Typography
                    variant="body2"
                    sx={{
                      color: "rgba(255,255,255,0.8)",
                      mb: 2,
                      height: "40px",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      display: "-webkit-box",
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: "vertical",
                    }}
                  >
                    {exam.description}
                  </Typography>

                  <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                    <Chip
                      icon={getStatusIcon(exam.status)}
                      label={exam.status}
                      color={getStatusColor(exam.status)}
                      size="small"
                    />
                    <Chip
                      icon={<Timer />}
                      label={`${exam.duration_minutes} min`}
                      variant="outlined"
                      size="small"
                      sx={{
                        color: "white",
                        borderColor: "rgba(255,255,255,0.3)",
                      }}
                    />
                  </Stack>

                  <Divider
                    sx={{ backgroundColor: "rgba(255,255,255,0.1)", mb: 2 }}
                  />

                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography
                        variant="caption"
                        sx={{ color: "rgba(255,255,255,0.6)" }}
                      >
                        Questions
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{ color: "white", fontWeight: 600 }}
                      >
                        {exam.total_questions || 0}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography
                        variant="caption"
                        sx={{ color: "rgba(255,255,255,0.6)" }}
                      >
                        Difficulty
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{ color: "white", fontWeight: 600 }}
                      >
                        {exam.difficulty_level}
                      </Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography
                        variant="caption"
                        sx={{ color: "rgba(255,255,255,0.6)" }}
                      >
                        Created
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{ color: "white", fontWeight: 600 }}
                      >
                        {formatDate(exam.created_at)}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </ExamCard>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        PaperProps={{
          sx: {
            background:
              "linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05))",
            backdropFilter: "blur(20px)",
            border: "1px solid rgba(255, 255, 255, 0.2)",
            borderRadius: "12px",
            color: "white",
          },
        }}
      >
        <MenuItem onClick={() => handleViewExam(selectedExam)}>
          <Visibility sx={{ mr: 1 }} />
          View Details
        </MenuItem>
        <MenuItem onClick={handleEditExam}>
          <Edit sx={{ mr: 1 }} />
          Edit Exam
        </MenuItem>
        <MenuItem onClick={handleDeleteClick} sx={{ color: "#ff6b6b" }}>
          <Delete sx={{ mr: 1 }} />
          Delete Exam
        </MenuItem>
      </Menu>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        PaperProps={{
          sx: {
            background:
              "linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05))",
            backdropFilter: "blur(20px)",
            border: "1px solid rgba(255, 255, 255, 0.2)",
            borderRadius: "20px",
            color: "white",
          },
        }}
      >
        <DialogTitle>Delete Exam</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{selectedExam?.title}"? This action
            cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setDeleteDialogOpen(false)}
            sx={{ color: "rgba(255,255,255,0.7)" }}
          >
            Cancel
          </Button>
          <Button
            onClick={() => handleDeleteExam(selectedExam?.id)}
            sx={{ color: "#ff6b6b" }}
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Exam Dialog */}
      <Dialog
        open={viewDialogOpen}
        onClose={() => {
          setViewDialogOpen(false);
          setExamDetails(null);
        }}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: {
            background:
              "linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05))",
            backdropFilter: "blur(20px)",
            border: "1px solid rgba(255, 255, 255, 0.2)",
            borderRadius: "20px",
            color: "white",
            maxHeight: "90vh",
          },
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Box display="flex" alignItems="center" gap={1}>
            <Visibility />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Exam Details: {selectedExam?.title}
            </Typography>
          </Box>
        </DialogTitle>

        <DialogContent sx={{ mt: 1 }}>
          {loadingDetails ? (
            <Box
              display="flex"
              justifyContent="center"
              alignItems="center"
              p={3}
            >
              <CircularProgress sx={{ color: "white" }} />
              <Typography sx={{ ml: 2, color: "white" }}>
                Loading exam details...
              </Typography>
            </Box>
          ) : examDetails ? (
            <Box>
              {/* Exam Information */}
              <Card
                sx={{
                  mb: 3,
                  background: "rgba(255,255,255,0.1)",
                  backdropFilter: "blur(10px)",
                  border: "1px solid rgba(255,255,255,0.2)",
                }}
              >
                <CardContent>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{
                      color: "white",
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                    }}
                  >
                    📋 Exam Information
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6} sm={3}>
                      <Typography
                        variant="body2"
                        sx={{ color: "rgba(255,255,255,0.7)" }}
                      >
                        Title:
                      </Typography>
                      <Typography variant="body1" sx={{ color: "white" }}>
                        {examDetails.exam_session.title}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography
                        variant="body2"
                        sx={{ color: "rgba(255,255,255,0.7)" }}
                      >
                        Questions:
                      </Typography>
                      <Typography variant="body1" sx={{ color: "white" }}>
                        {examDetails.exam_session.total_questions}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography
                        variant="body2"
                        sx={{ color: "rgba(255,255,255,0.7)" }}
                      >
                        Time Limit:
                      </Typography>
                      <Typography variant="body1" sx={{ color: "white" }}>
                        {Math.round(
                          examDetails.exam_session.time_limit_seconds / 60
                        )}{" "}
                        minutes
                      </Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography
                        variant="body2"
                        sx={{ color: "rgba(255,255,255,0.7)" }}
                      >
                        Status:
                      </Typography>
                      <Chip
                        label={
                          examDetails.exam_session.is_published
                            ? "Published"
                            : "Draft"
                        }
                        color={
                          examDetails.exam_session.is_published
                            ? "success"
                            : "default"
                        }
                        size="small"
                      />
                    </Grid>
                    {examDetails.exam_session.description && (
                      <Grid item xs={12}>
                        <Typography
                          variant="body2"
                          sx={{ color: "rgba(255,255,255,0.7)" }}
                        >
                          Description:
                        </Typography>
                        <Typography variant="body1" sx={{ color: "white" }}>
                          {examDetails.exam_session.description}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </CardContent>
              </Card>

              {/* Questions List */}
              <Card
                sx={{
                  background: "rgba(255,255,255,0.1)",
                  backdropFilter: "blur(10px)",
                  border: "1px solid rgba(255,255,255,0.2)",
                }}
              >
                <CardContent>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{
                      color: "white",
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                    }}
                  >
                    📝 Questions ({examDetails.questions.length})
                  </Typography>

                  {examDetails.questions.length > 0 ? (
                    <Box sx={{ maxHeight: 500, overflow: "auto", pr: 1 }}>
                      {examDetails.questions.map((question, index) => (
                        <Card
                          key={question.id}
                          sx={{
                            mb: 2,
                            background: "rgba(255,255,255,0.05)",
                            border: "1px solid rgba(255,255,255,0.1)",
                          }}
                        >
                          <CardContent>
                            <Box
                              display="flex"
                              justifyContent="space-between"
                              alignItems="flex-start"
                              mb={2}
                            >
                              <Typography
                                variant="subtitle1"
                                fontWeight="bold"
                                sx={{ color: "white" }}
                              >
                                Question {index + 1}
                              </Typography>
                              <Box display="flex" gap={1}>
                                {question.difficulty_level && (
                                  <Chip
                                    label={`Level ${question.difficulty_level}`}
                                    size="small"
                                    sx={{
                                      background: "rgba(255, 152, 0, 0.8)",
                                      color: "white",
                                    }}
                                  />
                                )}
                                {question.topic && (
                                  <Chip
                                    label={question.topic}
                                    size="small"
                                    variant="outlined"
                                    sx={{
                                      color: "white",
                                      borderColor: "rgba(255,255,255,0.3)",
                                    }}
                                  />
                                )}
                              </Box>
                            </Box>

                            <Typography
                              variant="body1"
                              paragraph
                              sx={{ color: "white", lineHeight: 1.6 }}
                            >
                              {question.question_text}
                            </Typography>

                            {/* Multiple Choice Options */}
                            {(question.option_a ||
                              question.option_b ||
                              question.option_c ||
                              question.option_d) && (
                              <Box
                                sx={{
                                  bgcolor: "rgba(255,255,255,0.05)",
                                  p: 2,
                                  borderRadius: 1,
                                  mb: 2,
                                  border: "1px solid rgba(255,255,255,0.1)",
                                }}
                              >
                                <Typography
                                  variant="subtitle2"
                                  gutterBottom
                                  sx={{ color: "rgba(255,255,255,0.8)" }}
                                >
                                  Options:
                                </Typography>
                                {question.option_a && (
                                  <Typography
                                    variant="body2"
                                    sx={{
                                      display: "flex",
                                      alignItems: "center",
                                      mb: 1,
                                      color: "white",
                                      p: 1,
                                      borderRadius: 1,
                                      background:
                                        question.correct_answer ===
                                        question.option_a
                                          ? "rgba(76, 175, 80, 0.2)"
                                          : "transparent",
                                    }}
                                  >
                                    <strong style={{ marginRight: "8px" }}>
                                      A.
                                    </strong>{" "}
                                    {question.option_a}
                                    {question.correct_answer ===
                                      question.option_a && (
                                      <Chip
                                        label="✓ Correct"
                                        size="small"
                                        sx={{
                                          ml: 1,
                                          background: "rgba(76, 175, 80, 0.8)",
                                          color: "white",
                                        }}
                                      />
                                    )}
                                  </Typography>
                                )}
                                {question.option_b && (
                                  <Typography
                                    variant="body2"
                                    sx={{
                                      display: "flex",
                                      alignItems: "center",
                                      mb: 1,
                                      color: "white",
                                      p: 1,
                                      borderRadius: 1,
                                      background:
                                        question.correct_answer ===
                                        question.option_b
                                          ? "rgba(76, 175, 80, 0.2)"
                                          : "transparent",
                                    }}
                                  >
                                    <strong style={{ marginRight: "8px" }}>
                                      B.
                                    </strong>{" "}
                                    {question.option_b}
                                    {question.correct_answer ===
                                      question.option_b && (
                                      <Chip
                                        label="✓ Correct"
                                        size="small"
                                        sx={{
                                          ml: 1,
                                          background: "rgba(76, 175, 80, 0.8)",
                                          color: "white",
                                        }}
                                      />
                                    )}
                                  </Typography>
                                )}
                                {question.option_c && (
                                  <Typography
                                    variant="body2"
                                    sx={{
                                      display: "flex",
                                      alignItems: "center",
                                      mb: 1,
                                      color: "white",
                                      p: 1,
                                      borderRadius: 1,
                                      background:
                                        question.correct_answer ===
                                        question.option_c
                                          ? "rgba(76, 175, 80, 0.2)"
                                          : "transparent",
                                    }}
                                  >
                                    <strong style={{ marginRight: "8px" }}>
                                      C.
                                    </strong>{" "}
                                    {question.option_c}
                                    {question.correct_answer ===
                                      question.option_c && (
                                      <Chip
                                        label="✓ Correct"
                                        size="small"
                                        sx={{
                                          ml: 1,
                                          background: "rgba(76, 175, 80, 0.8)",
                                          color: "white",
                                        }}
                                      />
                                    )}
                                  </Typography>
                                )}
                                {question.option_d && (
                                  <Typography
                                    variant="body2"
                                    sx={{
                                      display: "flex",
                                      alignItems: "center",
                                      mb: 1,
                                      color: "white",
                                      p: 1,
                                      borderRadius: 1,
                                      background:
                                        question.correct_answer ===
                                        question.option_d
                                          ? "rgba(76, 175, 80, 0.2)"
                                          : "transparent",
                                    }}
                                  >
                                    <strong style={{ marginRight: "8px" }}>
                                      D.
                                    </strong>{" "}
                                    {question.option_d}
                                    {question.correct_answer ===
                                      question.option_d && (
                                      <Chip
                                        label="✓ Correct"
                                        size="small"
                                        sx={{
                                          ml: 1,
                                          background: "rgba(76, 175, 80, 0.8)",
                                          color: "white",
                                        }}
                                      />
                                    )}
                                  </Typography>
                                )}
                              </Box>
                            )}

                            {/* Correct Answer for non-multiple choice */}
                            {!question.option_a &&
                              !question.option_b &&
                              !question.option_c &&
                              !question.option_d && (
                                <Box
                                  sx={{
                                    bgcolor: "rgba(76, 175, 80, 0.2)",
                                    p: 2,
                                    borderRadius: 1,
                                    border: "1px solid rgba(76, 175, 80, 0.3)",
                                  }}
                                >
                                  <Typography
                                    variant="body2"
                                    sx={{ color: "white" }}
                                  >
                                    <strong>Correct Answer:</strong>{" "}
                                    {question.correct_answer}
                                  </Typography>
                                </Box>
                              )}
                          </CardContent>
                        </Card>
                      ))}
                    </Box>
                  ) : (
                    <Alert
                      severity="warning"
                      sx={{
                        background: "rgba(255, 152, 0, 0.1)",
                        color: "white",
                        border: "1px solid rgba(255, 152, 0, 0.3)",
                        "& .MuiAlert-icon": { color: "white" },
                      }}
                    >
                      This exam has no questions linked to it. This might be due
                      to an error during exam creation.
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </Box>
          ) : (
            <Alert
              severity="error"
              sx={{
                background: "rgba(244, 67, 54, 0.1)",
                color: "white",
                border: "1px solid rgba(244, 67, 54, 0.3)",
                "& .MuiAlert-icon": { color: "white" },
              }}
            >
              Failed to load exam details. Please try again.
            </Alert>
          )}
        </DialogContent>

        <DialogActions sx={{ p: 3 }}>
          <Button
            onClick={() => {
              setViewDialogOpen(false);
              setExamDetails(null);
            }}
            sx={{ color: "rgba(255,255,255,0.7)" }}
          >
            Close
          </Button>
          {examDetails && examDetails.questions.length > 0 && (
            <StyledButton
              startIcon={<Edit />}
              onClick={() => {
                setViewDialogOpen(false);
                setEditDialogOpen(true);
              }}
            >
              Edit Exam
            </StyledButton>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box
        sx={{ borderBottom: 1, borderColor: "rgba(255,255,255,0.2)", mb: 3 }}
      >
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          sx={{
            "& .MuiTab-root": {
              color: "rgba(255,255,255,0.7)",
              fontWeight: 600,
              textTransform: "none",
            },
            "& .Mui-selected": {
              color: "white",
            },
            "& .MuiTabs-indicator": {
              backgroundColor: "white",
            },
          }}
        >
          <Tab icon={<Add />} label="Create Exam" />
          <Tab icon={<Assignment />} label="Manage Exams" />
        </Tabs>
      </Box>

      {activeTab === 0 && renderCreateTab()}
      {activeTab === 1 && renderManageTab()}

      {/* Success/Error Snackbars */}
      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={() => setSuccess(null)}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert
          onClose={() => setSuccess(null)}
          severity="success"
          sx={{ width: "100%" }}
        >
          {success}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert
          onClose={() => setError(null)}
          severity="error"
          sx={{ width: "100%" }}
        >
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ManageExams;
