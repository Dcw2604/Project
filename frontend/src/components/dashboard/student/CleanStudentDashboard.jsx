import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Typography,
  Button,
  Paper,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  LinearProgress,
  Chip,
} from "@mui/material";
import {
  Assignment,
  PlayArrow,
  CheckCircle,
  Error,
  Timer,
  School,
} from "@mui/icons-material";
import { useAuth } from "../../../hooks/useAuth";
import InteractiveExamInterface from "./InteractiveExamInterface";

const CleanStudentDashboard = () => {
  const { user } = useAuth();
  const [examState, setExamState] = useState("idle"); // idle, loading, in_progress, completed
  const [sessionId, setSessionId] = useState(null);
  const [examData, setExamData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const startExam = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("authToken");
      const response = await fetch(
        "http://127.0.0.1:8000/api/clean-exam/start/",
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Token ${token}`,
          },
        }
      );

      const data = await response.json();

      if (response.ok) {
        if (data.status === "completed") {
          setExamState("completed");
          setExamData(data);
        } else {
          setExamState("in_progress");
          setSessionId(data.session_id);
          setExamData(data);
        }
      } else {
        setError(data.error || "Failed to start exam");
      }
    } catch (err) {
      setError("Network error. Please try again.");
      console.error("Error starting exam:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleExamComplete = (summary) => {
    setExamState("completed");
    setExamData((prev) => ({ ...prev, summary }));
  };

  const resetExam = () => {
    setExamState("idle");
    setSessionId(null);
    setExamData(null);
    setError(null);
  };

  if (examState === "in_progress" && sessionId) {
    return (
      <InteractiveExamInterface
        sessionId={sessionId}
        examData={examData}
        onComplete={handleExamComplete}
        onError={setError}
      />
    );
  }

  if (examState === "completed" && examData) {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          p: 3,
        }}
      >
        <Container maxWidth="md">
          <Paper
            elevation={3}
            sx={{ p: 4, borderRadius: 3, textAlign: "center" }}
          >
            <CheckCircle sx={{ fontSize: 80, color: "success.main", mb: 2 }} />
            <Typography variant="h4" gutterBottom>
              Exam Completed!
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ mb: 3 }}>
              Great job, {user?.username}!
            </Typography>

            <Card sx={{ mb: 3, textAlign: "left" }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Results Summary
                </Typography>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mb: 1,
                  }}
                >
                  <Typography>Final Score:</Typography>
                  <Typography variant="h6" color="primary">
                    {examData.final_score?.toFixed(1)}%
                  </Typography>
                </Box>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mb: 1,
                  }}
                >
                  <Typography>Questions Answered:</Typography>
                  <Typography>
                    {examData.summary?.questions_answered || 0} /{" "}
                    {examData.summary?.total_questions || 0}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mb: 1,
                  }}
                >
                  <Typography>Correct Answers:</Typography>
                  <Typography color="success.main">
                    {examData.summary?.correct_answers || 0}
                  </Typography>
                </Box>
                {examData.summary?.total_time_minutes && (
                  <Box
                    sx={{ display: "flex", justifyContent: "space-between" }}
                  >
                    <Typography>Time Taken:</Typography>
                    <Typography>
                      {examData.summary.total_time_minutes.toFixed(1)} minutes
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>

            <Button
              variant="contained"
              size="large"
              startIcon={<PlayArrow />}
              onClick={resetExam}
              sx={{ mr: 2 }}
            >
              Take Another Exam
            </Button>
          </Paper>
        </Container>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        p: 3,
      }}
    >
      <Container maxWidth="md">
        <Paper
          elevation={3}
          sx={{ p: 4, borderRadius: 3, textAlign: "center" }}
        >
          <School sx={{ fontSize: 80, color: "primary.main", mb: 2 }} />
          <Typography variant="h3" gutterBottom>
            Interactive Exam
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
            Test your knowledge with questions generated from teacher-uploaded
            materials
          </Typography>

          <Card sx={{ mb: 4, textAlign: "left" }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Exam Features
              </Typography>
              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 2 }}>
                <Chip
                  icon={<Assignment />}
                  label="10 Questions"
                  color="primary"
                />
                <Chip
                  icon={<Timer />}
                  label="3 Attempts per Question"
                  color="secondary"
                />
                <Chip
                  icon={<CheckCircle />}
                  label="Progressive Hints"
                  color="success"
                />
              </Box>
              <Typography variant="body2" color="text.secondary">
                • Questions are generated from teacher-uploaded documents
                <br />
                • You have up to 3 attempts per question
                <br />
                • Get helpful hints after wrong answers
                <br />• Your progress is automatically saved
              </Typography>
            </CardContent>
          </Card>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Button
            variant="contained"
            size="large"
            startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
            onClick={startExam}
            disabled={loading}
            sx={{ px: 4, py: 1.5, fontSize: "1.1rem" }}
          >
            {loading ? "Starting Exam..." : "Start Interactive Exam"}
          </Button>
        </Paper>
      </Container>
    </Box>
  );
};

export default CleanStudentDashboard;
