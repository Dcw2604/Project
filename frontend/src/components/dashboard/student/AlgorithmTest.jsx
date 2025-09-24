import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  LinearProgress,
  styled,
  Container,
  Paper,
  Stack,
  Chip,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from "@mui/material";
import {
  PlayArrow,
  CheckCircle,
  Timer,
  QuestionAnswer,
  TrendingUp,
  Refresh,
  Psychology,
  Stop,
  Lightbulb,
  ExpandMore,
  Send,
} from "@mui/icons-material";

const StyledContainer = styled(Container)(({ theme }) => ({
  height: "calc(100vh - 80px)",
  paddingTop: "2rem",
  paddingBottom: "2rem",
  background: "transparent",
  overflow: "auto",
  "&::-webkit-scrollbar": {
    width: "8px",
  },
  "&::-webkit-scrollbar-track": {
    background: "rgba(255, 255, 255, 0.1)",
    borderRadius: "4px",
  },
  "&::-webkit-scrollbar-thumb": {
    background: "rgba(255, 255, 255, 0.3)",
    borderRadius: "4px",
    "&:hover": {
      background: "rgba(255, 255, 255, 0.5)",
    },
  },
}));

const GlassCard = styled(Card)(({ theme }) => ({
  background: "rgba(255, 255, 255, 0.1)",
  backdropFilter: "blur(20px)",
  border: "1px solid rgba(255, 255, 255, 0.2)",
  borderRadius: "20px",
  boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
  marginBottom: "1.5rem",
}));

const AlgorithmTest = () => {
  const [testStarted, setTestStarted] = useState(false);
  const [testCompleted, setTestCompleted] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [timeLeft, setTimeLeft] = useState(1800); // 30 minutes
  const [testResult, setTestResult] = useState(null);
  const [selectedLevel, setSelectedLevel] = useState(null);
  const [showLevelSelection, setShowLevelSelection] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hints, setHints] = useState([]);
  const [hintLevel, setHintLevel] = useState(0);
  const [evaluation, setEvaluation] = useState(null);
  const [correctAnswers, setCorrectAnswers] = useState(0);

  const difficultyLevels = [
    {
      id: "easy",
      name: "Easy",
      description: "Basic algorithms and simple data structures",
      color: "success",
      icon: "🌱",
    },
    {
      id: "normal",
      name: "Normal",
      description: "Moderate algorithmic problems",
      color: "warning",
      icon: "🌿",
    },
    {
      id: "hard",
      name: "Hard",
      description: "Complex algorithms and optimization",
      color: "error",
      icon: "🌳",
    },
  ];

  // Fetch algorithm questions from the API
  const fetchQuestions = async (difficultyLevel) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/questions/test/?difficulty_level=${difficultyLevel}&num_questions=5&subject=algorithms`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch questions");
      }

      const data = await response.json();

      if (data.questions && data.questions.length > 0) {
        setQuestions(data.questions);
      } else {
        // Fallback to sample algorithm questions
        setQuestions(getSampleAlgorithmQuestions(difficultyLevel));
        setError(
          "Using sample questions - no teacher questions available for this level"
        );
      }
    } catch (err) {
      console.error("Error fetching questions:", err);
      setError("Failed to load questions from server, using sample questions");
      setQuestions(getSampleAlgorithmQuestions(difficultyLevel));
    } finally {
      setLoading(false);
    }
  };

  // Sample algorithm questions as fallback
  const getSampleAlgorithmQuestions = (level) => {
    const sampleQuestions = {
      easy: [
        {
          id: 1,
          question:
            "Describe the steps to implement a binary search algorithm on a sorted array. What is its time complexity?",
          type: "algorithm_design",
          subject: "algorithms",
          difficulty: "easy",
          expected_approach:
            "Binary search divides the search space in half at each step",
          key_concepts: "divide and conquer, sorted array, logarithmic time",
          hints:
            "Think about how you can eliminate half of the array at each step",
          correct_answer:
            "Binary search works by repeatedly dividing the sorted array in half and comparing the target with the middle element",
        },
        {
          id: 2,
          question:
            "Explain how a stack data structure works and provide one common use case.",
          type: "data_structures",
          subject: "algorithms",
          difficulty: "easy",
          expected_approach: "LIFO (Last In, First Out) principle",
          key_concepts: "LIFO, push, pop, function calls",
          hints: "Think about how function calls are managed in programming",
          correct_answer:
            "Stack follows LIFO principle where elements are added and removed from the top",
        },
      ],
      normal: [
        {
          id: 1,
          question:
            "Design an algorithm to find the longest common subsequence between two strings. Explain your approach and analyze the time complexity.",
          type: "algorithm_design",
          subject: "algorithms",
          difficulty: "normal",
          expected_approach: "Dynamic programming approach with 2D table",
          key_concepts: "dynamic programming, subsequence, memoization",
          hints: "Consider using a 2D table to store intermediate results",
          correct_answer:
            "Use dynamic programming with a 2D table where dp[i][j] represents LCS length",
        },
      ],
      hard: [
        {
          id: 1,
          question:
            "Implement and explain Dijkstra's shortest path algorithm. Discuss optimization techniques and edge cases.",
          type: "algorithm_design",
          subject: "algorithms",
          difficulty: "hard",
          expected_approach: "Priority queue based greedy algorithm",
          key_concepts:
            "graph algorithms, priority queue, greedy approach, shortest path",
          hints:
            "Think about using a priority queue to always process the closest unvisited vertex",
          correct_answer:
            "Dijkstra's algorithm uses a priority queue to greedily select the closest unvisited vertex",
        },
      ],
    };

    return sampleQuestions[level] || [];
  };

  // Timer effect
  useEffect(() => {
    let timer;
    if (testStarted && !testCompleted && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            handleTestComplete();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [testStarted, testCompleted, timeLeft]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const handleLevelSelect = async (level) => {
    setSelectedLevel(level);
    setShowLevelSelection(false);

    // Fetch questions for the selected level
    await fetchQuestions(level);

    setTestStarted(true);
    setCurrentQuestion(0);
    setCurrentAnswer("");
    setTestCompleted(false);
    setTimeLeft(1800);
    setTestResult(null);
    setHints([]);
    setHintLevel(0);
    setEvaluation(null);
    setCorrectAnswers(0);
  };

  const handleStartTest = () => {
    setShowLevelSelection(true);
  };

  const getHint = async () => {
    if (hintLevel >= 3) return; // Max 3 hints per question

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/tests/get_hint/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Token ${localStorage.getItem("authToken")}`,
          },
          body: JSON.stringify({
            question_id: questions[currentQuestion].id,
            student_input: currentAnswer,
            hint_level: hintLevel + 1,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setHints([...hints, data.hint]);
        setHintLevel(data.hint_level);
      }
    } catch (err) {
      console.error("Error getting hint:", err);
    }
  };

  const evaluateAnswer = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/tests/evaluate_answer/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Token ${localStorage.getItem("authToken")}`,
          },
          body: JSON.stringify({
            question_id: questions[currentQuestion].id,
            answer: currentAnswer,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setEvaluation(data);

        if (data.is_correct) {
          setCorrectAnswers((prev) => prev + 1);
          // Auto-advance to next question after correct answer
          setTimeout(() => {
            if (currentQuestion < questions.length - 1) {
              handleNextQuestion();
            } else {
              handleTestComplete();
            }
          }, 2000);
        }
      }
    } catch (err) {
      console.error("Error evaluating answer:", err);
    }
  };

  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setCurrentAnswer("");
      setHints([]);
      setHintLevel(0);
      setEvaluation(null);
    } else {
      handleTestComplete();
    }
  };

  const handleTestComplete = () => {
    setTestCompleted(true);
    const score = (correctAnswers / questions.length) * 100;

    let assessedLevel = "Beginner";
    if (score >= 80) assessedLevel = "Advanced";
    else if (score >= 60) assessedLevel = "Intermediate";

    setTestResult({
      score: score,
      correct: correctAnswers,
      total: questions.length,
      level: assessedLevel,
      timeUsed: 1800 - timeLeft,
    });
  };

  const handleRetakeTest = () => {
    setTestStarted(false);
    setTestCompleted(false);
    setCurrentQuestion(0);
    setCurrentAnswer("");
    setTimeLeft(1800);
    setTestResult(null);
    setSelectedLevel(null);
    setQuestions([]);
    setHints([]);
    setHintLevel(0);
    setEvaluation(null);
    setCorrectAnswers(0);
  };

  // Level Selection Screen
  if (!testStarted && !showLevelSelection) {
    return (
      <StyledContainer maxWidth="md">
        <GlassCard>
          <CardContent sx={{ textAlign: "center", p: 4 }}>
            <Psychology sx={{ fontSize: "4rem", color: "#fff", mb: 2 }} />
            <Typography
              variant="h3"
              component="h1"
              sx={{ color: "#fff", fontWeight: "bold", mb: 2 }}
            >
              Algorithm Knowledge Test
            </Typography>
            <Typography
              variant="h6"
              sx={{ color: "rgba(255,255,255,0.8)", mb: 4, lineHeight: 1.6 }}
            >
              Test your understanding of algorithms and data structures with
              open-ended questions. Get AI-powered hints when you need help!
            </Typography>

            <Stack
              direction="row"
              spacing={3}
              justifyContent="center"
              flexWrap="wrap"
            >
              <Chip
                icon={<QuestionAnswer />}
                label="Open-ended Questions"
                color="primary"
              />
              <Chip
                icon={<Lightbulb />}
                label="AI Hints Available"
                color="secondary"
              />
              <Chip icon={<Timer />} label="30 Minutes" color="info" />
            </Stack>

            <Button
              variant="contained"
              size="large"
              startIcon={<PlayArrow />}
              onClick={handleStartTest}
              sx={{
                mt: 4,
                px: 4,
                py: 1.5,
                fontSize: "1.1rem",
                background: "linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)",
                borderRadius: "25px",
                boxShadow: "0 3px 5px 2px rgba(33, 203, 243, .3)",
              }}
            >
              Start Algorithm Test
            </Button>
          </CardContent>
        </GlassCard>
      </StyledContainer>
    );
  }

  // Level Selection
  if (showLevelSelection) {
    return (
      <StyledContainer maxWidth="lg">
        <GlassCard>
          <CardContent sx={{ p: 4 }}>
            <Typography
              variant="h4"
              component="h2"
              sx={{ color: "#fff", textAlign: "center", mb: 4 }}
            >
              Choose Your Difficulty Level
            </Typography>

            <Stack spacing={3}>
              {difficultyLevels.map((level) => (
                <Card
                  key={level.id}
                  sx={{
                    background: "rgba(255, 255, 255, 0.05)",
                    border: "1px solid rgba(255, 255, 255, 0.2)",
                    cursor: "pointer",
                    transition: "all 0.3s ease",
                    "&:hover": {
                      background: "rgba(255, 255, 255, 0.15)",
                      transform: "translateY(-2px)",
                    },
                  }}
                  onClick={() => handleLevelSelect(level.id)}
                >
                  <CardContent
                    sx={{ display: "flex", alignItems: "center", p: 3 }}
                  >
                    <Typography sx={{ fontSize: "2rem", mr: 3 }}>
                      {level.icon}
                    </Typography>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography
                        variant="h5"
                        sx={{ color: "#fff", fontWeight: "bold" }}
                      >
                        {level.name}
                      </Typography>
                      <Typography
                        variant="body1"
                        sx={{ color: "rgba(255,255,255,0.7)" }}
                      >
                        {level.description}
                      </Typography>
                    </Box>
                    <Chip
                      label={level.name}
                      color={level.color}
                      sx={{ ml: 2 }}
                    />
                  </CardContent>
                </Card>
              ))}
            </Stack>
          </CardContent>
        </GlassCard>
      </StyledContainer>
    );
  }

  // Test in Progress
  if (testStarted && !testCompleted && questions.length > 0) {
    const question = questions[currentQuestion];

    return (
      <StyledContainer maxWidth="lg">
        {/* Progress Header */}
        <GlassCard>
          <CardContent sx={{ p: 3 }}>
            <Stack
              direction="row"
              justifyContent="space-between"
              alignItems="center"
              mb={2}
            >
              <Typography variant="h6" sx={{ color: "#fff" }}>
                Question {currentQuestion + 1} of {questions.length}
              </Typography>
              <Stack direction="row" spacing={2} alignItems="center">
                <Timer sx={{ color: "#fff" }} />
                <Typography variant="h6" sx={{ color: "#fff" }}>
                  {formatTime(timeLeft)}
                </Typography>
              </Stack>
            </Stack>

            <LinearProgress
              variant="determinate"
              value={((currentQuestion + 1) / questions.length) * 100}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: "rgba(255,255,255,0.2)",
                "& .MuiLinearProgress-bar": {
                  background:
                    "linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)",
                },
              }}
            />
          </CardContent>
        </GlassCard>

        {/* Question */}
        <GlassCard>
          <CardContent sx={{ p: 4 }}>
            <Stack spacing={3}>
              <Box>
                <Chip
                  label={`${question.difficulty} • ${question.type?.replace(
                    "_",
                    " "
                  )}`}
                  color="primary"
                  sx={{ mb: 2 }}
                />
                <Typography
                  variant="h5"
                  sx={{ color: "#fff", fontWeight: "bold", mb: 3 }}
                >
                  {question.question}
                </Typography>
              </Box>

              <TextField
                multiline
                rows={6}
                fullWidth
                value={currentAnswer}
                onChange={(e) => setCurrentAnswer(e.target.value)}
                placeholder="Type your answer here... Explain your approach step by step."
                sx={{
                  "& .MuiOutlinedInput-root": {
                    color: "#fff",
                    backgroundColor: "rgba(255, 255, 255, 0.05)",
                    "& fieldset": {
                      borderColor: "rgba(255, 255, 255, 0.3)",
                    },
                    "&:hover fieldset": {
                      borderColor: "rgba(255, 255, 255, 0.5)",
                    },
                    "&.Mui-focused fieldset": {
                      borderColor: "#2196F3",
                    },
                  },
                  "& .MuiInputLabel-root": {
                    color: "rgba(255, 255, 255, 0.7)",
                  },
                  "& .MuiInputBase-input::placeholder": {
                    color: "rgba(255, 255, 255, 0.5)",
                  },
                }}
              />

              <Stack direction="row" spacing={2} justifyContent="space-between">
                <Button
                  variant="outlined"
                  startIcon={<Lightbulb />}
                  onClick={getHint}
                  disabled={hintLevel >= 3 || !currentAnswer.trim()}
                  sx={{
                    color: "#fff",
                    borderColor: "rgba(255, 255, 255, 0.3)",
                    "&:hover": {
                      borderColor: "#fff",
                      backgroundColor: "rgba(255, 255, 255, 0.1)",
                    },
                  }}
                >
                  Get Hint ({hintLevel}/3)
                </Button>

                <Button
                  variant="contained"
                  endIcon={<Send />}
                  onClick={evaluateAnswer}
                  disabled={!currentAnswer.trim()}
                  sx={{
                    background:
                      "linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)",
                    borderRadius: "25px",
                  }}
                >
                  Submit Answer
                </Button>
              </Stack>
            </Stack>
          </CardContent>
        </GlassCard>

        {/* Hints */}
        {hints.length > 0 && (
          <GlassCard>
            <CardContent sx={{ p: 3 }}>
              <Typography
                variant="h6"
                sx={{
                  color: "#fff",
                  mb: 2,
                  display: "flex",
                  alignItems: "center",
                }}
              >
                <Lightbulb sx={{ mr: 1 }} />
                Hints
              </Typography>
              {hints.map((hint, index) => (
                <Accordion
                  key={index}
                  sx={{ backgroundColor: "rgba(255, 255, 255, 0.05)", mb: 1 }}
                >
                  <AccordionSummary
                    expandIcon={<ExpandMore sx={{ color: "#fff" }} />}
                  >
                    <Typography sx={{ color: "#fff" }}>
                      Hint {index + 1}
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography sx={{ color: "rgba(255,255,255,0.8)" }}>
                      {hint}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              ))}
            </CardContent>
          </GlassCard>
        )}

        {/* Evaluation */}
        {evaluation && (
          <GlassCard>
            <CardContent sx={{ p: 3 }}>
              <Alert
                severity={evaluation.is_correct ? "success" : "warning"}
                sx={{
                  backgroundColor: evaluation.is_correct
                    ? "rgba(76, 175, 80, 0.1)"
                    : "rgba(255, 152, 0, 0.1)",
                  color: "#fff",
                  "& .MuiAlert-icon": {
                    color: evaluation.is_correct ? "#4caf50" : "#ff9800",
                  },
                }}
              >
                <Typography variant="h6" sx={{ mb: 1 }}>
                  {evaluation.is_correct
                    ? "Correct! 🎉"
                    : "Not quite right, but keep trying! 💪"}
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {evaluation.feedback}
                </Typography>
                {!evaluation.is_correct && (
                  <>
                    <Typography
                      variant="body2"
                      sx={{ mb: 1, fontWeight: "bold" }}
                    >
                      Expected approach:
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {evaluation.expected_approach}
                    </Typography>
                    <Button
                      variant="outlined"
                      onClick={() => setEvaluation(null)}
                      sx={{
                        color: "#fff",
                        borderColor: "rgba(255, 255, 255, 0.3)",
                        "&:hover": {
                          borderColor: "#fff",
                          backgroundColor: "rgba(255, 255, 255, 0.1)",
                        },
                      }}
                    >
                      Try Again
                    </Button>
                  </>
                )}
              </Alert>
            </CardContent>
          </GlassCard>
        )}
      </StyledContainer>
    );
  }

  // Test Completed
  if (testCompleted && testResult) {
    return (
      <StyledContainer maxWidth="md">
        <GlassCard>
          <CardContent sx={{ textAlign: "center", p: 4 }}>
            <CheckCircle sx={{ fontSize: "4rem", color: "#4caf50", mb: 2 }} />
            <Typography
              variant="h3"
              component="h1"
              sx={{ color: "#fff", fontWeight: "bold", mb: 2 }}
            >
              Test Completed!
            </Typography>

            <Stack spacing={3} sx={{ mt: 4 }}>
              <Box>
                <Typography
                  variant="h2"
                  sx={{ color: "#2196F3", fontWeight: "bold" }}
                >
                  {testResult.score.toFixed(1)}%
                </Typography>
                <Typography variant="h5" sx={{ color: "#fff", mt: 1 }}>
                  Your Algorithm Knowledge Level:{" "}
                  <strong>{testResult.level}</strong>
                </Typography>
              </Box>

              <Stack direction="row" spacing={4} justifyContent="center">
                <Box sx={{ textAlign: "center" }}>
                  <Typography
                    variant="h4"
                    sx={{ color: "#4caf50", fontWeight: "bold" }}
                  >
                    {testResult.correct}
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{ color: "rgba(255,255,255,0.8)" }}
                  >
                    Correct
                  </Typography>
                </Box>
                <Box sx={{ textAlign: "center" }}>
                  <Typography
                    variant="h4"
                    sx={{ color: "#f44336", fontWeight: "bold" }}
                  >
                    {testResult.total - testResult.correct}
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{ color: "rgba(255,255,255,0.8)" }}
                  >
                    Incorrect
                  </Typography>
                </Box>
                <Box sx={{ textAlign: "center" }}>
                  <Typography
                    variant="h4"
                    sx={{ color: "#2196F3", fontWeight: "bold" }}
                  >
                    {Math.floor(testResult.timeUsed / 60)}m
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{ color: "rgba(255,255,255,0.8)" }}
                  >
                    Time Used
                  </Typography>
                </Box>
              </Stack>
            </Stack>

            <Button
              variant="contained"
              size="large"
              startIcon={<Refresh />}
              onClick={handleRetakeTest}
              sx={{
                mt: 4,
                px: 4,
                py: 1.5,
                fontSize: "1.1rem",
                background: "linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)",
                borderRadius: "25px",
              }}
            >
              Take Test Again
            </Button>
          </CardContent>
        </GlassCard>
      </StyledContainer>
    );
  }

  // Loading state
  if (loading) {
    return (
      <StyledContainer maxWidth="md">
        <GlassCard>
          <CardContent sx={{ textAlign: "center", p: 4 }}>
            <CircularProgress sx={{ color: "#2196F3", mb: 2 }} />
            <Typography variant="h6" sx={{ color: "#fff" }}>
              Loading algorithm questions...
            </Typography>
          </CardContent>
        </GlassCard>
      </StyledContainer>
    );
  }

  return null;
};

export default AlgorithmTest;
