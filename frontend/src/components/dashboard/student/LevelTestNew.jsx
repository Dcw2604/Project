import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Button, 
  RadioGroup,
  FormControlLabel,
  Radio,
  LinearProgress,
  styled,
  Container,
  Paper,
  Stack,
  Chip,
  Alert,
  Grid,
  CircularProgress
} from '@mui/material';
import { 
  PlayArrow, 
  CheckCircle, 
  Timer, 
  QuestionAnswer,
  TrendingUp,
  Refresh,
  EmojiEvents,
  Psychology,
  Stop
} from '@mui/icons-material';

const StyledContainer = styled(Container)(({ theme }) => ({
  height: 'calc(100vh - 80px)',
  paddingTop: '2rem',
  paddingBottom: '2rem',
  background: 'transparent',
  overflow: 'auto',
  '&::-webkit-scrollbar': {
    width: '8px',
  },
  '&::-webkit-scrollbar-track': {
    background: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '4px',
  },
  '&::-webkit-scrollbar-thumb': {
    background: 'rgba(255, 255, 255, 0.3)',
    borderRadius: '4px',
    '&:hover': {
      background: 'rgba(255, 255, 255, 0.5)',
    },
  },
}));

const GlassCard = styled(Card)(({ theme }) => ({
  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05))',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  borderRadius: '20px',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
  marginBottom: '1.5rem',
  color: 'white'
}));

const HeaderCard = styled(Paper)(({ theme }) => ({
  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1))',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  borderRadius: '24px',
  padding: '2rem',
  marginBottom: '2rem',
  color: 'white',
  textAlign: 'center'
}));

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: '16px',
  padding: '12px 24px',
  fontWeight: 600,
  textTransform: 'none',
  fontSize: '1rem',
  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1))',
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(255, 255, 255, 0.3)',
  color: 'white',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.2))',
    transform: 'translateY(-2px)',
    boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)',
  }
}));

const QuestionCard = styled(GlassCard)(({ theme }) => ({
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: '0 16px 48px rgba(0, 0, 0, 0.2)',
  }
}));

const LevelTest = () => {
  const [testStarted, setTestStarted] = useState(false);
  const [testCompleted, setTestCompleted] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(1800); // 30 minutes
  const [testResult, setTestResult] = useState(null);
  const [selectedLevel, setSelectedLevel] = useState(null);
  const [showLevelSelection, setShowLevelSelection] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const difficultyLevels = [
    { id: '3', name: 'Basic', description: 'Fundamental concepts and simple calculations', color: 'success', icon: '🌱' },
    { id: '4', name: 'Intermediate', description: 'Moderate complexity problems', color: 'warning', icon: '🌿' },
    { id: '5', name: 'Advanced', description: 'Complex problem-solving', color: 'error', icon: '🌳' }
  ];

  // Fetch questions from the API
  const fetchQuestions = async (difficultyLevel) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/questions/test/?difficulty_level=${difficultyLevel}&num_questions=10`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch questions');
      }
      
      const data = await response.json();
      
      if (data.questions && data.questions.length > 0) {
        setQuestions(data.questions);
      } else {
        // Fallback to sample questions if no teacher questions available
        setQuestions(getSampleQuestions(difficultyLevel));
        setError('Using sample questions - no teacher questions available for this level');
      }
    } catch (err) {
      console.error('Error fetching questions:', err);
      setError('Failed to load questions from server, using sample questions');
      setQuestions(getSampleQuestions(difficultyLevel));
    } finally {
      setLoading(false);
    }
  };

  // Sample questions as fallback
  const getSampleQuestions = (level) => {
    const sampleQuestions = {
      '3': [
        {
          id: 1,
          question: "What is 15 + 27?",
          options: ["42", "41", "43", "40"],
          correct: 0,
          subject: "Mathematics",
          difficulty: "Basic"
        },
        {
          id: 2,
          question: "What is 8 × 7?",
          options: ["54", "56", "58", "52"],
          correct: 1,
          subject: "Mathematics",
          difficulty: "Basic"
        }
      ],
      '4': [
        {
          id: 1,
          question: "Solve for x: 2x + 5 = 13",
          options: ["x = 4", "x = 3", "x = 5", "x = 6"],
          correct: 0,
          subject: "Mathematics",
          difficulty: "Intermediate"
        },
        {
          id: 2,
          question: "What is the area of a circle with radius 4?",
          options: ["16π", "8π", "4π", "12π"],
          correct: 0,
          subject: "Mathematics",
          difficulty: "Intermediate"
        }
      ],
      '5': [
        {
          id: 1,
          question: "Find the derivative of f(x) = 3x² + 2x - 1",
          options: ["6x + 2", "6x - 2", "3x + 2", "6x + 1"],
          correct: 0,
          subject: "Mathematics",
          difficulty: "Advanced"
        },
        {
          id: 2,
          question: "Solve: x² - 5x + 6 = 0",
          options: ["x = 2, 3", "x = 1, 6", "x = 2, 4", "x = 1, 5"],
          correct: 0,
          subject: "Mathematics",
          difficulty: "Advanced"
        }
      ]
    };
    
    return sampleQuestions[level] || [];
  };

  useEffect(() => {
    let timer;
    if (testStarted && !testCompleted && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft(prev => {
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
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleLevelSelect = async (level) => {
    setSelectedLevel(level);
    setShowLevelSelection(false);
    
    // Fetch questions for the selected level
    await fetchQuestions(level);
    
    setTestStarted(true);
    setCurrentQuestion(0);
    setAnswers({});
    setTestCompleted(false);
    setTimeLeft(1800);
    setTestResult(null);
  };

  const handleStartTest = () => {
    setShowLevelSelection(true);
  };

  const handleStopTest = () => {
    if (window.confirm('Are you sure you want to stop the test? Your progress will be lost.')) {
      setTestStarted(false);
      setTestCompleted(false);
      setCurrentQuestion(0);
      setAnswers({});
      setTimeLeft(1800);
      setTestResult(null);
      setSelectedLevel(null);
      setShowLevelSelection(false);
      setQuestions([]);
      setError(null);
    }
  };

  const handleAnswerChange = (questionId, answerIndex) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answerIndex
    }));
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    } else {
      handleTestComplete();
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const handleTestComplete = async () => {
    setTestCompleted(true);
    
    // Calculate results
    let correct = 0;
    const questionIds = [];
    questions.forEach(q => {
      questionIds.push(q.id);
      if (answers[q.id] === q.correct) {
        correct++;
      }
    });
    
    const percentage = (correct / questions.length) * 100;
    let level = 'Beginner';
    let levelColor = '#EF4444';
    
    if (percentage >= 90) {
      level = 'Advanced';
      levelColor = '#10B981';
    } else if (percentage >= 70) {
      level = 'Intermediate';
      levelColor = '#F59E0B';
    } else if (percentage >= 50) {
      level = 'Elementary';
      levelColor = '#6366F1';
    }
    
    const timeUsed = 1800 - timeLeft;
    
    const testResults = {
      correct,
      total: questions.length,
      percentage: Math.round(percentage),
      level,
      levelColor,
      timeUsed
    };
    
    setTestResult(testResults);
    
    // Submit results to backend
    try {
      const token = localStorage.getItem('authToken');
      if (token) {
        const response = await fetch('http://127.0.0.1:8000/api/tests/submit_results/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${token}`,
          },
          body: JSON.stringify({
            difficulty_level: selectedLevel,
            total_questions: questions.length,
            correct_answers: correct,
            time_taken_seconds: timeUsed,
            percentage_score: percentage,
            assessed_level: level,
            questions_used: questionIds
          }),
        });
        
        if (response.ok) {
          console.log('Test results submitted successfully');
        } else {
          console.error('Failed to submit test results');
        }
      }
    } catch (error) {
      console.error('Error submitting test results:', error);
    }
  };

  const handleRetakeTest = () => {
    setTestStarted(false);
    setTestCompleted(false);
    setCurrentQuestion(0);
    setAnswers({});
    setTimeLeft(1800);
    setTestResult(null);
    setSelectedLevel(null);
    setShowLevelSelection(false);
    setQuestions([]);
    setError(null);
  };

  // Don't start test if no questions available
  if (showLevelSelection) {
    return (
      <StyledContainer maxWidth="md">
        <HeaderCard elevation={0}>
          <Psychology sx={{ fontSize: '3rem', mb: 2 }} />
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Choose Your Test Level
          </Typography>
          <Typography variant="body1" sx={{ opacity: 0.8 }}>
            Select the difficulty level for your assessment
          </Typography>
        </HeaderCard>

        <Grid container spacing={3}>
          {difficultyLevels.map((level) => (
            <Grid item xs={12} md={4} key={level.id}>
              <GlassCard 
                sx={{ 
                  cursor: 'pointer',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
                  }
                }}
                onClick={() => handleLevelSelect(level.id)}
              >
                <CardContent sx={{ textAlign: 'center', p: 3 }}>
                  <Typography variant="h2" sx={{ mb: 2 }}>
                    {level.icon}
                  </Typography>
                  <Typography variant="h5" fontWeight={600} gutterBottom>
                    {level.name}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.8, mb: 2 }}>
                    {level.description}
                  </Typography>
                  <Chip 
                    label={`Level ${level.id}`}
                    color={level.color}
                    sx={{ fontWeight: 600 }}
                  />
                </CardContent>
              </GlassCard>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ textAlign: 'center', mt: 3 }}>
          <ActionButton 
            startIcon={<Stop />}
            onClick={() => setShowLevelSelection(false)}
          >
            Cancel
          </ActionButton>
        </Box>
      </StyledContainer>
    );
  }

  if (loading) {
    return (
      <StyledContainer maxWidth="md">
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <CircularProgress sx={{ color: 'white', mb: 2 }} size={60} />
          <Typography variant="h6" color="white">
            Loading test questions...
          </Typography>
        </Box>
      </StyledContainer>
    );
  }

  if (testCompleted && testResult) {
    return (
      <StyledContainer maxWidth="md">
        <HeaderCard elevation={0}>
          <EmojiEvents sx={{ fontSize: '4rem', mb: 2, color: testResult.levelColor }} />
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Test Completed!
          </Typography>
          <Typography variant="body1" sx={{ opacity: 0.8 }}>
            Here are your results
          </Typography>
        </HeaderCard>

        <GlassCard>
          <CardContent sx={{ p: 4 }}>
            <Grid container spacing={4} alignItems="center">
              <Grid item xs={12} md={6}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h2" fontWeight={700} sx={{ color: testResult.levelColor, mb: 1 }}>
                    {testResult.percentage}%
                  </Typography>
                  <Typography variant="h6" gutterBottom>
                    {testResult.correct} out of {testResult.total} correct
                  </Typography>
                  <Chip 
                    label={testResult.level}
                    sx={{ 
                      bgcolor: testResult.levelColor,
                      color: 'white',
                      fontWeight: 600,
                      fontSize: '1rem',
                      px: 2,
                      py: 1
                    }}
                  />
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Stack spacing={2}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body1">Time Used:</Typography>
                    <Typography variant="body1" fontWeight={600}>
                      {formatTime(testResult.timeUsed)}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body1">Accuracy:</Typography>
                    <Typography variant="body1" fontWeight={600}>
                      {testResult.percentage}%
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body1">Level:</Typography>
                    <Typography variant="body1" fontWeight={600} sx={{ color: testResult.levelColor }}>
                      {testResult.level}
                    </Typography>
                  </Box>
                </Stack>
              </Grid>
            </Grid>

            <Box sx={{ textAlign: 'center', mt: 4 }}>
              <ActionButton 
                startIcon={<Refresh />}
                onClick={handleRetakeTest}
                sx={{ mr: 2 }}
              >
                Retake Test
              </ActionButton>
            </Box>
          </CardContent>
        </GlassCard>
      </StyledContainer>
    );
  }

  if (testStarted && questions.length > 0) {
    const currentQuestionData = questions[currentQuestion];
    const progress = ((currentQuestion + 1) / questions.length) * 100;

    return (
      <StyledContainer maxWidth="md">
        {error && (
          <Alert severity="warning" sx={{ mb: 2, bgcolor: 'rgba(255, 193, 7, 0.1)', color: 'white' }}>
            {error}
          </Alert>
        )}
        
        {/* Header with timer and progress */}
        <Paper sx={{ 
          p: 2, 
          mb: 3, 
          background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05))',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '16px',
          color: 'white'
        }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">
              Question {currentQuestion + 1} of {questions.length}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Timer />
              <Typography variant="h6" fontWeight={600}>
                {formatTime(timeLeft)}
              </Typography>
            </Box>
          </Stack>
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            sx={{ 
              height: 8, 
              borderRadius: 4,
              bgcolor: 'rgba(255, 255, 255, 0.2)',
              '& .MuiLinearProgress-bar': {
                bgcolor: 'linear-gradient(135deg, #4CAF50, #2196F3)'
              }
            }}
          />
        </Paper>

        {/* Question Card */}
        <QuestionCard>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ mb: 3 }}>
              <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                <Chip 
                  label={currentQuestionData.subject}
                  size="small"
                  sx={{ bgcolor: 'rgba(33, 150, 243, 0.2)', color: 'white' }}
                />
                <Chip 
                  label={currentQuestionData.difficulty}
                  size="small"
                  sx={{ bgcolor: 'rgba(76, 175, 80, 0.2)', color: 'white' }}
                />
              </Stack>
              <Typography variant="h5" fontWeight={600} gutterBottom>
                {currentQuestionData.question}
              </Typography>
            </Box>

            <RadioGroup
              value={answers[currentQuestionData.id] ?? ''}
              onChange={(e) => handleAnswerChange(currentQuestionData.id, parseInt(e.target.value))}
            >
              {currentQuestionData.options.map((option, index) => (
                <FormControlLabel
                  key={index}
                  value={index}
                  control={<Radio sx={{ color: 'white' }} />}
                  label={
                    <Typography variant="body1" sx={{ color: 'white' }}>
                      {option}
                    </Typography>
                  }
                  sx={{ 
                    py: 1,
                    px: 2,
                    margin: '8px 0',
                    borderRadius: '12px',
                    transition: 'all 0.2s',
                    '&:hover': {
                      bgcolor: 'rgba(255, 255, 255, 0.1)'
                    }
                  }}
                />
              ))}
            </RadioGroup>

            <Stack direction="row" justifyContent="space-between" sx={{ mt: 4 }}>
              <ActionButton 
                onClick={handlePrevious}
                disabled={currentQuestion === 0}
                sx={{ visibility: currentQuestion === 0 ? 'hidden' : 'visible' }}
              >
                Previous
              </ActionButton>
              
              <ActionButton onClick={handleStopTest} color="error">
                <Stop sx={{ mr: 1 }} />
                Stop Test
              </ActionButton>

              <ActionButton 
                onClick={handleNext}
                disabled={answers[currentQuestionData.id] === undefined}
                variant="contained"
                sx={{ 
                  bgcolor: answers[currentQuestionData.id] !== undefined ? 'rgba(76, 175, 80, 0.8)' : 'rgba(255, 255, 255, 0.1)',
                  '&:hover': {
                    bgcolor: answers[currentQuestionData.id] !== undefined ? 'rgba(76, 175, 80, 1)' : 'rgba(255, 255, 255, 0.2)',
                  }
                }}
              >
                {currentQuestion === questions.length - 1 ? 'Complete Test' : 'Next'}
              </ActionButton>
            </Stack>
          </CardContent>
        </QuestionCard>
      </StyledContainer>
    );
  }

  // Initial state - show start test button
  return (
    <StyledContainer maxWidth="md">
      <HeaderCard elevation={0}>
        <QuestionAnswer sx={{ fontSize: '4rem', mb: 2 }} />
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Mathematics Level Assessment
        </Typography>
        <Typography variant="body1" sx={{ opacity: 0.8, mb: 3 }}>
          Test your knowledge with questions from your teachers' curriculum
        </Typography>
        <Typography variant="body2" sx={{ opacity: 0.7 }}>
          This test uses questions generated by your teachers from course materials
        </Typography>
      </HeaderCard>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <GlassCard>
            <CardContent sx={{ textAlign: 'center' }}>
              <Timer sx={{ fontSize: '2.5rem', mb: 2, color: '#2196F3' }} />
              <Typography variant="h6" fontWeight={600} gutterBottom>
                30 Minutes
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Time limit for the test
              </Typography>
            </CardContent>
          </GlassCard>
        </Grid>

        <Grid item xs={12} md={4}>
          <GlassCard>
            <CardContent sx={{ textAlign: 'center' }}>
              <QuestionAnswer sx={{ fontSize: '2.5rem', mb: 2, color: '#4CAF50' }} />
              <Typography variant="h6" fontWeight={600} gutterBottom>
                10 Questions
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                From teacher curriculum
              </Typography>
            </CardContent>
          </GlassCard>
        </Grid>

        <Grid item xs={12} md={4}>
          <GlassCard>
            <CardContent sx={{ textAlign: 'center' }}>
              <TrendingUp sx={{ fontSize: '2.5rem', mb: 2, color: '#FF9800' }} />
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Instant Results
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Get your level assessment
              </Typography>
            </CardContent>
          </GlassCard>
        </Grid>
      </Grid>

      <Box sx={{ textAlign: 'center' }}>
        <ActionButton 
          size="large"
          startIcon={<PlayArrow />}
          onClick={handleStartTest}
          sx={{ 
            px: 4, 
            py: 2,
            fontSize: '1.2rem',
            background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.8), rgba(33, 150, 243, 0.8))',
            '&:hover': {
              background: 'linear-gradient(135deg, rgba(76, 175, 80, 1), rgba(33, 150, 243, 1))',
            }
          }}
        >
          Start Level Test
        </ActionButton>
      </Box>
    </StyledContainer>
  );
};

export default LevelTest;
