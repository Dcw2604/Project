import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Paper,
  Card,
  CardContent,
  LinearProgress,
  Alert,
  Chip,
  CircularProgress,
  Fade,
  Divider,
} from "@mui/material";
import {
  Send,
  CheckCircle,
  Error,
  Lightbulb,
  Timer,
  NavigateNext,
  Refresh,
} from "@mui/icons-material";

const InteractiveExamInterface = ({
  sessionId,
  examData,
  onComplete,
  onError,
}) => {
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [answer, setAnswer] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [attemptsLeft, setAttemptsLeft] = useState(3);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (examData?.current_question) {
      setCurrentQuestion(examData.current_question);
      setLoading(false);
    }
  }, [examData]);

  const submitAnswer = async () => {
    if (!answer.trim()) return;

    setSubmitting(true);
    setError(null);

    try {
      const token = localStorage.getItem("authToken");
      const response = await fetch(
        "http://127.0.0.1:8000/api/clean-exam/answer/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Token ${token}`,
          },
          body: JSON.stringify({
            session_id: sessionId,
            question_id: currentQuestion.question_id,
            answer: answer.trim(),
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setFeedback({
          correct: data.correct,
          message: data.message,
          hint: data.hint,
          remaining_attempts: data.remaining_attempts,
          reveal_answer: data.reveal_answer,
          move_to_next: data.move_to_next,
        });

        setAttemptsLeft(data.remaining_attempts);

        if (data.move_to_next) {
          // Move to next question after a delay
          setTimeout(() => {
            if (data.correct || data.reveal_answer) {
              loadNextQuestion();
            }
          }, 2000);
        }
      } else {
        setError(data.error || "Failed to submit answer");
      }
    } catch (err) {
      setError("Network error. Please try again.");
      console.error("Error submitting answer:", err);
    } finally {
      setSubmitting(false);
    }
  };

  const loadNextQuestion = async () => {
    setLoading(true);
    setAnswer("");
    setFeedback(null);
    setAttemptsLeft(3);
    setError(null);

    try {
      const token = localStorage.getItem("authToken");
      const response = await fetch(
        `http://127.0.0.1:8000/api/clean-exam/state/?session_id=${sessionId}`,
        {
          headers: {
            Authorization: `Token ${token}`,
          },
        }
      );

      const data = await response.json();

      if (response.ok) {
        if (data.status === "completed") {
          onComplete(data.summary);
        } else if (data.current_question) {
          setCurrentQuestion(data.current_question);
        } else {
          onComplete(data.summary);
        }
      } else {
        setError(data.error || "Failed to load next question");
      }
    } catch (err) {
      setError("Network error. Please try again.");
      console.error("Error loading next question:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !submitting && answer.trim()) {
      submitAnswer();
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "50vh",
        }}
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (!currentQuestion) {
    return (
      <Box sx={{ textAlign: "center", p: 4 }}>
        <Typography variant="h6">No questions available</Typography>
        <Button onClick={loadNextQuestion} startIcon={<Refresh />}>
          Refresh
        </Button>
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
        {/* Progress Header */}
        <Paper elevation={3} sx={{ p: 2, mb: 3, borderRadius: 2 }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 2,
            }}
          >
            <Typography variant="h6">
              {examData?.exam_title || "Interactive Exam"}
            </Typography>
            <Chip
              label={`Question ${currentQuestion.index} of ${currentQuestion.total}`}
              color="primary"
              variant="outlined"
            />
          </Box>
          <LinearProgress
            variant="determinate"
            value={(currentQuestion.index / currentQuestion.total) * 100}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Paper>

        {/* Question Card */}
        <Paper elevation={3} sx={{ p: 4, mb: 3, borderRadius: 3 }}>
          <Typography variant="h6" gutterBottom color="primary">
            Question {currentQuestion.index}
          </Typography>
          <Typography
            variant="body1"
            sx={{ mb: 3, fontSize: "1.1rem", lineHeight: 1.6 }}
          >
            {currentQuestion.question_text}
          </Typography>

          {/* Answer Input */}
          <TextField
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            placeholder="Enter your answer here..."
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={submitting || feedback?.move_to_next}
            sx={{ mb: 2 }}
          />

          {/* Submit Button */}
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <Chip
                icon={<Timer />}
                label={`${attemptsLeft} attempts left`}
                color={
                  attemptsLeft === 1
                    ? "error"
                    : attemptsLeft === 2
                    ? "warning"
                    : "default"
                }
                variant="outlined"
              />
              {currentQuestion.difficulty && (
                <Chip
                  label={currentQuestion.difficulty}
                  size="small"
                  color="secondary"
                />
              )}
            </Box>
            <Button
              variant="contained"
              size="large"
              startIcon={submitting ? <CircularProgress size={20} /> : <Send />}
              onClick={submitAnswer}
              disabled={!answer.trim() || submitting || feedback?.move_to_next}
            >
              {submitting ? "Submitting..." : "Submit Answer"}
            </Button>
          </Box>
        </Paper>

        {/* Feedback */}
        {feedback && (
          <Fade in={true}>
            <Paper
              elevation={3}
              sx={{
                p: 3,
                mb: 3,
                borderRadius: 3,
                backgroundColor: feedback.correct
                  ? "success.light"
                  : "error.light",
                color: feedback.correct
                  ? "success.contrastText"
                  : "error.contrastText",
              }}
            >
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                {feedback.correct ? (
                  <CheckCircle sx={{ mr: 1, fontSize: 30 }} />
                ) : (
                  <Error sx={{ mr: 1, fontSize: 30 }} />
                )}
                <Typography variant="h6">{feedback.message}</Typography>
              </Box>

              {feedback.hint && (
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                    <Lightbulb sx={{ mr: 1, fontSize: 20 }} />
                    <Typography variant="subtitle2">Hint:</Typography>
                  </Box>
                  <Typography variant="body2">{feedback.hint}</Typography>
                </Box>
              )}

              {feedback.reveal_answer && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Correct Answer:
                  </Typography>
                  <Typography variant="body2" sx={{ fontStyle: "italic" }}>
                    {feedback.reveal_answer}
                  </Typography>
                </Box>
              )}

              {feedback.move_to_next && (
                <Box sx={{ display: "flex", alignItems: "center", mt: 2 }}>
                  <NavigateNext sx={{ mr: 1 }} />
                  <Typography variant="body2">
                    Moving to next question...
                  </Typography>
                </Box>
              )}
            </Paper>
          </Fade>
        )}

        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Progress Stats */}
        {examData?.progress && (
          <Paper elevation={1} sx={{ p: 2, borderRadius: 2 }}>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-around",
                textAlign: "center",
              }}
            >
              <Box>
                <Typography variant="h6" color="primary">
                  {examData.progress.questions_answered}
                </Typography>
                <Typography variant="caption">Answered</Typography>
              </Box>
              <Box>
                <Typography variant="h6" color="success.main">
                  {examData.progress.correct_answers}
                </Typography>
                <Typography variant="caption">Correct</Typography>
              </Box>
              <Box>
                <Typography variant="h6" color="text.secondary">
                  {examData.progress.percentage?.toFixed(1)}%
                </Typography>
                <Typography variant="caption">Progress</Typography>
              </Box>
            </Box>
          </Paper>
        )}
      </Container>
    </Box>
  );
};

export default InteractiveExamInterface;
