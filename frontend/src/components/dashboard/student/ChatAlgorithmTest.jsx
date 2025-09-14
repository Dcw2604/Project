import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  LinearProgress,
  IconButton,
  Tooltip,
  Grid,
  Stack,
} from "@mui/material";
import {
  Send,
  Lightbulb,
  Psychology,
  MenuBook,
  TipsAndUpdates,
  Timer,
  Assessment,
  Person,
  SmartToy,
} from "@mui/icons-material";

// API Configuration
const API_BASE_URL = "http://127.0.0.1:8000/api";
const getAuthHeaders = () => ({
  Authorization: `Token ${localStorage.getItem("authToken")}`,
  "Content-Type": "application/json",
});

const ChatAlgorithmTest = () => {
  // Core state management
  const [examSession, setExamSession] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState(null);

  // UI state
  const [showExamSelection, setShowExamSelection] = useState(true);
  const [loading, setLoading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  // Available exams
  const [availableExams, setAvailableExams] = useState([]);

  // Chat messages
  const [messages, setMessages] = useState([]);
  const [currentInput, setCurrentInput] = useState("");

  // Learning progress
  const [studentProgress, setStudentProgress] = useState({
    correctAnswers: 0,
    totalAttempts: 0,
    hintsUsed: 0,
    questionsCompleted: 0,
    score: 0,
  });

  // Educational features
  const [hintLevel, setHintLevel] = useState(0);
  const [maxHints] = useState(3);
  const [questionAttempts, setQuestionAttempts] = useState(0);
  const [maxAttempts] = useState(3);

  // Timer
  const [timeLeft, setTimeLeft] = useState(null);
  const [timerActive, setTimerActive] = useState(false);

  const messagesEndRef = useRef(null);
  // Effects
  useEffect(() => {
    loadAvailableExams();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    let timer;
    if (timerActive && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            handleTimeUp();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [timerActive, timeLeft]);

  // Utility functions
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const formatTime = (seconds) => {
    if (!seconds) return "";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // Load available exam sessions
  const loadAvailableExams = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/exam-sessions/list/`, {
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        const data = await response.json();
        console.log("📚 Available exams:", data);
        setAvailableExams(data.exam_sessions || []);
      } else {
        console.error("Failed to load exams:", response.status);
        addTutorMessage(
          "❌ Failed to load available exams. Please try again.",
          "error"
        );
      }
    } catch (error) {
      console.error("Error loading exams:", error);
      addTutorMessage(
        "❌ Error connecting to server. Please check your connection.",
        "error"
      );
    } finally {
      setLoading(false);
    }
  };

  // Start exam session
  const startExamSession = async (examId) => {
    try {
      setLoading(true);
      console.log("🎯 Starting exam:", examId);

      const response = await fetch(
        `${API_BASE_URL}/exam-sessions/${examId}/start/`,
        {
          method: "POST",
          headers: getAuthHeaders(),
        }
      );

      if (response.ok) {
        const examData = await response.json();
        console.log("📊 Exam data:", examData);

        if (examData.questions && examData.questions.length > 0) {
          setExamSession(examData.exam_session);
          setQuestions(examData.questions);
          setCurrentQuestionIndex(0);
          setShowExamSelection(false);
          setHintLevel(0);
          setQuestionAttempts(0);

          // Set up timer if exam has time limit
          if (examData.exam_session.duration_minutes) {
            setTimeLeft(examData.exam_session.duration_minutes * 60);
            setTimerActive(true);
          }

          // Initialize progress
          setStudentProgress({
            correctAnswers: 0,
            totalAttempts: 0,
            hintsUsed: 0,
            questionsCompleted: 0,
            score: 0,
          });

          // Welcome message
          const welcomeMessage = {
            id: Date.now(),
            text: `🎓 Welcome to your knowledge assessment: "${
              examData.exam_session.title
            }"!\n\nI'm here to help you learn through guided questions. Don't worry about making mistakes - they're part of the learning process! I'll provide hints and explanations to guide you.\n\n📚 Total Questions: ${
              examData.questions.length
            }${
              examData.exam_session.duration_minutes
                ? `\n⏰ Time Limit: ${examData.exam_session.duration_minutes} minutes`
                : ""
            }\n\nLet's begin!`,
            sender: "tutor",
            timestamp: new Date().toISOString(),
            type: "welcome",
          };

          setMessages([welcomeMessage]);

          // Present first question
          setTimeout(() => {
            presentQuestion(examData.questions[0], 0);
          }, 2000);
        } else {
          addTutorMessage(
            "❌ This exam has no questions available. Please contact your teacher.",
            "error"
          );
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to start exam");
      }
    } catch (error) {
      console.error("Failed to start exam:", error);
      addTutorMessage(`❌ Failed to start the exam: ${error.message}`, "error");
    } finally {
      setLoading(false);
    }
  };

  // Educational functions
  const addTutorMessage = (text, type = "info") => {
    const message = {
      id: Date.now(),
      text,
      sender: "tutor",
      timestamp: new Date().toISOString(),
      type,
    };
    setMessages((prev) => [...prev, message]);
  };

  const presentQuestion = (question, questionIndex) => {
    setCurrentQuestion(question);
    setHintLevel(0);
    setQuestionAttempts(0);

    const questionMessage = {
      id: Date.now(),
      text: `📝 **Question ${questionIndex + 1} of ${questions.length}**\n\n${
        question.question_text || question.question
      }`,
      sender: "tutor",
      timestamp: new Date().toISOString(),
      type: "question",
      questionData: question,
    };

    // Add multiple choice options if available
    if (question.options && question.options.length > 0) {
      const validOptions = question.options.filter(
        (option) => option && option.trim()
      );
      if (validOptions.length > 0) {
        questionMessage.text += "\n\n**Choose the best answer:**\n";
        validOptions.forEach((option, index) => {
          questionMessage.text += `${String.fromCharCode(
            65 + index
          )}. ${option}\n`;
        });
        questionMessage.text +=
          "\n💡 Type the letter (A, B, C, or D) or explain your reasoning.";
      }
    } else {
      questionMessage.text +=
        "\n\n💭 Please provide your answer and explain your thinking.";
    }

    setMessages((prev) => [...prev, questionMessage]);
  };

  const provideHint = () => {
    if (!currentQuestion || hintLevel >= maxHints) return;

    const hints = generateContextualHints(currentQuestion, hintLevel);
    setHintLevel((prev) => prev + 1);

    const hintMessage = {
      id: Date.now(),
      text: `💡 **Hint ${hintLevel + 1}/${maxHints}:**\n\n${hints}`,
      sender: "tutor",
      timestamp: new Date().toISOString(),
      type: "hint",
    };

    setMessages((prev) => [...prev, hintMessage]);
    setStudentProgress((prev) => ({
      ...prev,
      hintsUsed: prev.hintsUsed + 1,
    }));
  };

  const generateContextualHints = (question, hintLevel) => {
    const questionText = question.question_text || question.question;
    const topic = question.topic || "the subject matter";

    const hints = [
      `Think about the key concept being asked. This question is testing your understanding of ${topic}. What was the main point discussed about this in the study material?`,
      `Consider the context from the document. Look for keywords in the question that relate to specific information provided. What details were mentioned about this topic?`,
      `Let me narrow it down for you. The answer relates to ${topic}. If this is multiple choice, eliminate the options that don't directly connect to the main concept discussed in the material.`,
    ];

    return (
      hints[hintLevel] ||
      "You're very close! Think about the most important information that was emphasized in the study material."
    );
  };

  const evaluateAnswer = async (studentAnswer) => {
    setIsProcessing(true);
    setQuestionAttempts((prev) => prev + 1);

    setStudentProgress((prev) => ({
      ...prev,
      totalAttempts: prev.totalAttempts + 1,
    }));

    try {
      const evaluation = evaluateStudentAnswer(currentQuestion, studentAnswer);

      if (evaluation.isCorrect) {
        // Correct answer
        const successMessage = {
          id: Date.now(),
          text: `🎉 **Excellent work!** That's absolutely correct!\n\n**Why this is right:**\n${
            evaluation.explanation
          }\n\n**Key Learning Point:**\n${
            evaluation.keyLearning
          }\n\n${generateEncouragement()}`,
          sender: "tutor",
          timestamp: new Date().toISOString(),
          type: "success",
        };

        setMessages((prev) => [...prev, successMessage]);
        setStudentProgress((prev) => ({
          ...prev,
          correctAnswers: prev.correctAnswers + 1,
          questionsCompleted: prev.questionsCompleted + 1,
          score: Math.round(
            ((prev.correctAnswers + 1) / (prev.questionsCompleted + 1)) * 100
          ),
        }));

        // Move to next question
        setTimeout(() => {
          moveToNextQuestion();
        }, 3000);
      } else {
        // Incorrect answer
        if (questionAttempts >= maxAttempts) {
          // Max attempts reached
          const finalAnswerMessage = {
            id: Date.now(),
            text: `🎯 **The correct answer is: ${currentQuestion.correct_answer}**\n\n**Explanation:**\n${evaluation.fullExplanation}\n\n**What you learned:**\n${evaluation.keyLearning}\n\nDon't worry! This is how we learn - by understanding our mistakes. Let's continue!`,
            sender: "tutor",
            timestamp: new Date().toISOString(),
            type: "final_answer",
          };

          setMessages((prev) => [...prev, finalAnswerMessage]);

          setStudentProgress((prev) => ({
            ...prev,
            questionsCompleted: prev.questionsCompleted + 1,
            score: Math.round(
              (prev.correctAnswers / (prev.questionsCompleted + 1)) * 100
            ),
          }));

          setTimeout(() => {
            moveToNextQuestion();
          }, 4000);
        } else {
          // Still have attempts left
          const feedbackMessage = {
            id: Date.now(),
            text: `🤔 **That's not quite right, but you're thinking!**\n\n**What you might be considering:** ${
              evaluation.commonMistake
            }\n\n**Think about this:** ${
              evaluation.guidance
            }\n\n💪 **Attempts remaining:** ${
              maxAttempts - questionAttempts
            }\n\n${
              hintLevel < maxHints
                ? "💡 Would you like a hint, or do you want to try again?"
                : "🔄 Give it another try!"
            }`,
            sender: "tutor",
            timestamp: new Date().toISOString(),
            type: "feedback",
          };

          setMessages((prev) => [...prev, feedbackMessage]);
        }
      }
    } catch (error) {
      console.error("Error evaluating answer:", error);
      addTutorMessage(
        "❌ Sorry, I had trouble evaluating your answer. Please try again.",
        "error"
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const evaluateStudentAnswer = (question, studentAnswer) => {
    const correctAnswer = question.correct_answer;
    const studentAnswerClean = studentAnswer.toLowerCase().trim();
    const correctAnswerClean = correctAnswer.toLowerCase().trim();

    // Check if answer is correct
    const isCorrect =
      studentAnswerClean === correctAnswerClean ||
      studentAnswerClean.includes(correctAnswerClean) ||
      (question.options &&
        studentAnswerClean.match(/^[a-d]$/i) &&
        question.options[studentAnswerClean.charCodeAt(0) - 97] ===
          correctAnswer);

    const topic = question.topic || "this concept";

    return {
      isCorrect,
      explanation: isCorrect
        ? `You correctly identified "${correctAnswer}" as the answer. This demonstrates your solid understanding of ${topic}.`
        : `The correct answer is "${correctAnswer}". Let me explain why this is the right choice.`,
      keyLearning: `This question tests your knowledge of ${topic}, which is a fundamental concept in the study material.`,
      commonMistake: `This is a common area where students need more practice. The key is understanding the relationship between the question and the source material.`,
      guidance: `Focus on the specific details mentioned in the original document. Look for direct connections between the question and the information provided.`,
      fullExplanation: `"${correctAnswer}" is the correct answer because it directly corresponds to the information provided in the study material about ${topic}. This concept is important because it forms the foundation for understanding more complex ideas in this subject area.`,
    };
  };

  const generateEncouragement = () => {
    const encouragements = [
      "🌟 You're demonstrating great understanding!",
      "💪 Your analytical thinking is improving!",
      "🎯 You're mastering these concepts well!",
      "🚀 Excellent progress on your learning journey!",
      "🧠 Your knowledge is really developing!",
    ];
    return encouragements[Math.floor(Math.random() * encouragements.length)];
  };

  const moveToNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      const nextIndex = currentQuestionIndex + 1;
      setCurrentQuestionIndex(nextIndex);

      setTimeout(() => {
        addTutorMessage(
          `📖 Great! Let's continue building your knowledge with the next question.`
        );
        setTimeout(() => {
          presentQuestion(questions[nextIndex], nextIndex);
        }, 1500);
      }, 1000);
    } else {
      completeKnowledgeTest();
    }
  };

  const completeKnowledgeTest = () => {
    setTimerActive(false);
    const finalScore = Math.round(
      (studentProgress.correctAnswers / questions.length) * 100
    );
    const performance =
      finalScore >= 80
        ? "Outstanding"
        : finalScore >= 70
        ? "Good"
        : finalScore >= 60
        ? "Satisfactory"
        : "Needs Improvement";

    const completionMessage = {
      id: Date.now(),
      text: `🎓 **Knowledge Assessment Complete!**\n\n**Your Performance Summary:**\n\n📊 **Score:** ${finalScore}% (${performance})\n✅ **Correct Answers:** ${
        studentProgress.correctAnswers
      }/${questions.length}\n💡 **Hints Used:** ${
        studentProgress.hintsUsed
      }\n🔄 **Total Attempts:** ${
        studentProgress.totalAttempts
      }\n\n**What this means:**\n${generatePerformanceAnalysis(
        finalScore
      )}\n\n**Next Steps:**\n${generateRecommendations(
        finalScore
      )}\n\n🌟 Remember: Every question you answered helped reinforce your understanding of "${
        examSession.title
      }". Keep up the great work!`,
      sender: "tutor",
      timestamp: new Date().toISOString(),
      type: "completion",
    };

    setMessages((prev) => [...prev, completionMessage]);
  };

  const generatePerformanceAnalysis = (score) => {
    if (score >= 80) {
      return "You demonstrate excellent mastery of the material! Your understanding of the key concepts is very strong.";
    } else if (score >= 70) {
      return "You have a good grasp of most concepts with room for strengthening in a few areas.";
    } else if (score >= 60) {
      return "You understand the basic concepts but would benefit from reviewing the material to strengthen your knowledge.";
    } else {
      return "This assessment shows areas where additional study would be very helpful. Don't be discouraged - focus on understanding the concepts step by step.";
    }
  };

  const generateRecommendations = (score) => {
    if (score >= 80) {
      return "• Try more advanced topics\n• Help other students understand these concepts\n• Explore related subjects";
    } else if (score >= 70) {
      return "• Review the areas where you used hints\n• Practice similar questions\n• Discuss challenging concepts with your teacher";
    } else {
      return "• Re-read the study material carefully\n• Ask your teacher for additional resources\n• Take the assessment again after studying\n• Focus on understanding rather than memorizing";
    }
  };

  const handleTimeUp = () => {
    setTimerActive(false);
    addTutorMessage(
      "⏰ Time's up! Let's see how you did on the questions you completed.",
      "info"
    );
    completeKnowledgeTest();
  };

  const handleSendMessage = async () => {
    if (!currentInput.trim() || isProcessing) return;

    const userMessage = {
      id: Date.now(),
      text: currentInput,
      sender: "student",
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const userInput = currentInput.toLowerCase().trim();
    const originalInput = currentInput;
    setCurrentInput("");

    // Handle special commands
    if (userInput === "hint" && currentQuestion && hintLevel < maxHints) {
      provideHint();
      return;
    }

    // Evaluate the answer
    if (currentQuestion) {
      await evaluateAnswer(originalInput);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  // Render exam selection screen
  if (showExamSelection) {
    return (
      <Box
        sx={{ height: "100%", display: "flex", flexDirection: "column", p: 3 }}
      >
        <Typography
          variant="h4"
          gutterBottom
          sx={{ color: "white", textAlign: "center", mb: 1 }}
        >
          🧠 Knowledge Assessment Center
        </Typography>

        <Typography
          variant="subtitle1"
          sx={{ color: "rgba(255,255,255,0.8)", textAlign: "center", mb: 4 }}
        >
          Choose an assessment to test your knowledge. I'll guide you through
          the questions and help you learn!
        </Typography>

        {loading ? (
          <Box display="flex" justifyContent="center" mt={4}>
            <CircularProgress sx={{ color: "white" }} size={60} />
            <Typography sx={{ ml: 2, color: "white", alignSelf: "center" }}>
              Loading available assessments...
            </Typography>
          </Box>
        ) : (
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              gap: 3,
              maxWidth: 900,
              mx: "auto",
            }}
          >
            {availableExams.length > 0 ? (
              availableExams.map((exam) => (
                <Card
                  key={exam.id}
                  sx={{
                    background: "rgba(255,255,255,0.1)",
                    backdropFilter: "blur(10px)",
                    border: "1px solid rgba(255,255,255,0.2)",
                    transition: "all 0.3s ease",
                    "&:hover": {
                      background: "rgba(255,255,255,0.15)",
                      transform: "translateY(-2px)",
                      boxShadow: "0 8px 32px rgba(0,0,0,0.3)",
                    },
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box
                      display="flex"
                      justifyContent="space-between"
                      alignItems="flex-start"
                      mb={2}
                    >
                      <Box flex={1}>
                        <Typography
                          variant="h5"
                          sx={{
                            color: "white",
                            mb: 1,
                            display: "flex",
                            alignItems: "center",
                            gap: 1,
                          }}
                        >
                          <Assessment /> {exam.title}
                        </Typography>
                        <Typography
                          variant="body1"
                          sx={{ color: "rgba(255,255,255,0.8)", mb: 2 }}
                        >
                          {exam.description ||
                            "Test your knowledge and understanding of key concepts"}
                        </Typography>
                      </Box>
                    </Box>

                    <Grid container spacing={2} alignItems="center">
                      <Grid item xs={12} sm={6}>
                        <Box display="flex" gap={1} flexWrap="wrap">
                          <Chip
                            icon={<Assessment />}
                            label={`${
                              exam.total_questions || exam.num_questions || 0
                            } Questions`}
                            size="small"
                            sx={{
                              background: "rgba(33, 150, 243, 0.8)",
                              color: "white",
                            }}
                          />
                          <Chip
                            icon={<Timer />}
                            label={`${
                              exam.duration_minutes ||
                              Math.round((exam.time_limit_seconds || 3600) / 60)
                            } min`}
                            size="small"
                            sx={{
                              background: "rgba(76, 175, 80, 0.8)",
                              color: "white",
                            }}
                          />
                          {exam.difficulty_level && (
                            <Chip
                              label={exam.difficulty_level}
                              size="small"
                              sx={{
                                background: "rgba(255, 152, 0, 0.8)",
                                color: "white",
                              }}
                            />
                          )}
                        </Box>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Box display="flex" justifyContent="flex-end">
                          <Button
                            variant="contained"
                            onClick={() => startExamSession(exam.id)}
                            sx={{
                              background:
                                "linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)",
                              px: 4,
                              py: 1.5,
                              fontSize: "1.1rem",
                              boxShadow: "0 4px 20px rgba(33, 150, 243, 0.4)",
                              "&:hover": {
                                background:
                                  "linear-gradient(45deg, #1976D2 30%, #1BA9D1 90%)",
                                boxShadow: "0 6px 25px rgba(33, 150, 243, 0.6)",
                              },
                            }}
                            startIcon={<Psychology />}
                          >
                            Start Assessment
                          </Button>
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              ))
            ) : (
              <Alert
                severity="info"
                sx={{
                  background: "rgba(33, 150, 243, 0.1)",
                  color: "white",
                  border: "1px solid rgba(33, 150, 243, 0.3)",
                  "& .MuiAlert-icon": { color: "white" },
                }}
              >
                <Typography variant="h6" gutterBottom>
                  No Assessments Available
                </Typography>
                <Typography>
                  Your teacher hasn't created any knowledge assessments yet.
                  Check back later or contact your teacher for more information.
                </Typography>
              </Alert>
            )}
          </Box>
        )}
      </Box>
    );
  }

  // Render interactive chat interface
  return (
    <Box sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      {/* Header with progress */}
      <Paper
        sx={{
          p: 2,
          background: "rgba(255,255,255,0.1)",
          backdropFilter: "blur(10px)",
          borderRadius: 0,
          borderBottom: "1px solid rgba(255,255,255,0.2)",
        }}
      >
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          mb={1}
        >
          <Box>
            <Typography
              variant="h6"
              sx={{
                color: "white",
                display: "flex",
                alignItems: "center",
                gap: 1,
              }}
            >
              <Psychology /> Knowledge Assessment - {examSession?.title}
            </Typography>
            <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.7)" }}>
              Question {currentQuestionIndex + 1} of {questions.length} • Score:{" "}
              {studentProgress.score}%
              {timeLeft && ` • Time: ${formatTime(timeLeft)}`}
            </Typography>
          </Box>
          <Box display="flex" gap={1}>
            <Tooltip title={`Get hint (${maxHints - hintLevel} remaining)`}>
              <IconButton
                onClick={provideHint}
                disabled={
                  !currentQuestion ||
                  hintLevel >= maxHints ||
                  questionAttempts >= maxAttempts
                }
                sx={{
                  color:
                    hintLevel >= maxHints ? "rgba(255,255,255,0.3)" : "white",
                  background:
                    hintLevel >= maxHints ? "none" : "rgba(255,255,255,0.1)",
                }}
              >
                <Lightbulb />
              </IconButton>
            </Tooltip>
            <Tooltip title="Back to assessments">
              <IconButton
                onClick={() => setShowExamSelection(true)}
                sx={{ color: "white", background: "rgba(255,255,255,0.1)" }}
              >
                <MenuBook />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Progress indicators */}
        <Box display="flex" gap={2} alignItems="center">
          <Box flex={1}>
            <Typography
              variant="caption"
              sx={{ color: "rgba(255,255,255,0.7)" }}
            >
              Progress
            </Typography>
            <LinearProgress
              variant="determinate"
              value={(currentQuestionIndex / questions.length) * 100}
              sx={{
                backgroundColor: "rgba(255,255,255,0.2)",
                "& .MuiLinearProgress-bar": {
                  background:
                    "linear-gradient(45deg, #4caf50 30%, #8bc34a 90%)",
                },
              }}
            />
          </Box>
          <Box textAlign="center" minWidth={80}>
            <Typography
              variant="caption"
              sx={{ color: "rgba(255,255,255,0.7)" }}
            >
              Correct
            </Typography>
            <Typography variant="h6" sx={{ color: "#4caf50" }}>
              {studentProgress.correctAnswers}/
              {studentProgress.questionsCompleted}
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* Messages area */}
      <Box sx={{ flex: 1, overflow: "auto", p: 2 }}>
        {messages.map((message) => (
          <Box key={message.id} sx={{ mb: 3 }}>
            <Box
              sx={{
                display: "flex",
                justifyContent:
                  message.sender === "student" ? "flex-end" : "flex-start",
                mb: 1,
              }}
            >
              <Box
                sx={{
                  maxWidth: "85%",
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 1.5,
                  flexDirection:
                    message.sender === "student" ? "row-reverse" : "row",
                }}
              >
                <Avatar
                  sx={{
                    width: 40,
                    height: 40,
                    bgcolor:
                      message.sender === "student"
                        ? "primary.main"
                        : message.type === "success"
                        ? "#4caf50"
                        : message.type === "error"
                        ? "#f44336"
                        : message.type === "hint"
                        ? "#ff9800"
                        : "#2196f3",
                    fontSize: "1.2rem",
                  }}
                >
                  {message.sender === "student"
                    ? "👤"
                    : message.type === "success"
                    ? "🎉"
                    : message.type === "hint"
                    ? "💡"
                    : message.type === "error"
                    ? "❌"
                    : message.type === "completion"
                    ? "🎓"
                    : "🧠"}
                </Avatar>

                <Paper
                  sx={{
                    p: 3,
                    backgroundColor:
                      message.sender === "student"
                        ? "rgba(33, 150, 243, 0.8)"
                        : "rgba(255,255,255,0.1)",
                    color: "white",
                    backdropFilter: "blur(10px)",
                    border:
                      message.type === "success"
                        ? "2px solid #4caf50"
                        : message.type === "hint"
                        ? "2px solid #ff9800"
                        : message.type === "error"
                        ? "2px solid #f44336"
                        : message.type === "question"
                        ? "2px solid #2196f3"
                        : "1px solid rgba(255,255,255,0.2)",
                    borderRadius: 2,
                    boxShadow: "0 4px 20px rgba(0,0,0,0.3)",
                  }}
                >
                  <Typography
                    variant="body1"
                    sx={{
                      whiteSpace: "pre-wrap",
                      lineHeight: 1.6,
                      "& strong": { fontWeight: "bold" },
                      fontSize: message.type === "question" ? "1.1rem" : "1rem",
                    }}
                  >
                    {message.text.replace(/\*\*(.*?)\*\*/g, "$1")}
                  </Typography>

                  <Typography
                    variant="caption"
                    sx={{ opacity: 0.7, mt: 2, display: "block" }}
                  >
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </Typography>
                </Paper>
              </Box>
            </Box>
          </Box>
        ))}
        <div ref={messagesEndRef} />
      </Box>

      {/* Input area */}
      <Paper
        sx={{
          p: 2,
          background: "rgba(255,255,255,0.1)",
          backdropFilter: "blur(10px)",
          borderRadius: 0,
          borderTop: "1px solid rgba(255,255,255,0.2)",
        }}
      >
        <Box display="flex" gap={2} alignItems="flex-end">
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              !currentQuestion
                ? "Assessment not started..."
                : questionAttempts >= maxAttempts
                ? "Moving to next question..."
                : hintLevel < maxHints
                ? "Type your answer or 'hint' for help..."
                : "Type your answer..."
            }
            disabled={
              isProcessing ||
              !currentQuestion ||
              questionAttempts >= maxAttempts
            }
            sx={{
              "& .MuiOutlinedInput-root": {
                backgroundColor: "rgba(255,255,255,0.1)",
                color: "white",
                "& fieldset": { borderColor: "rgba(255,255,255,0.3)" },
                "&:hover fieldset": { borderColor: "rgba(255,255,255,0.5)" },
                "&.Mui-focused fieldset": { borderColor: "white" },
              },
              "& .MuiInputBase-input::placeholder": {
                color: "rgba(255,255,255,0.7)",
              },
              "& .MuiInputBase-input": { fontSize: "1.1rem" },
            }}
          />
          <Button
            variant="contained"
            onClick={handleSendMessage}
            disabled={
              !currentInput.trim() ||
              isProcessing ||
              !currentQuestion ||
              questionAttempts >= maxAttempts
            }
            sx={{
              minWidth: 60,
              height: 56,
              background: "linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)",
              boxShadow: "0 4px 20px rgba(33, 150, 243, 0.4)",
              "&:hover": {
                background: "linear-gradient(45deg, #1976D2 30%, #1BA9D1 90%)",
              },
              "&:disabled": {
                background: "rgba(255,255,255,0.1)",
                color: "rgba(255,255,255,0.3)",
              },
            }}
          >
            {isProcessing ? (
              <CircularProgress size={24} sx={{ color: "white" }} />
            ) : (
              <Send />
            )}
          </Button>
        </Box>

        {/* Help text */}
        {currentQuestion && questionAttempts < maxAttempts && (
          <Box
            mt={2}
            display="flex"
            justifyContent="space-between"
            alignItems="center"
          >
            <Box display="flex" gap={2}>
              {hintLevel < maxHints && (
                <Button
                  size="small"
                  onClick={provideHint}
                  startIcon={<TipsAndUpdates />}
                  sx={{
                    color: "rgba(255,255,255,0.8)",
                    "&:hover": { background: "rgba(255,255,255,0.1)" },
                  }}
                >
                  Get Hint ({maxHints - hintLevel} left)
                </Button>
              )}
            </Box>
            <Typography
              variant="caption"
              sx={{ color: "rgba(255,255,255,0.6)" }}
            >
              Attempts: {questionAttempts}/{maxAttempts}
            </Typography>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default ChatAlgorithmTest;
