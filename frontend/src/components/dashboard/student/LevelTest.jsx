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
  Grid
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
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [testCompleted, setTestCompleted] = useState(false);
  const [timeLeft, setTimeLeft] = useState(1800); // 30 minutes
  const [testResult, setTestResult] = useState(null);
  const [selectedLevel, setSelectedLevel] = useState(null);
  const [showLevelSelection, setShowLevelSelection] = useState(false);

  // Math questions organized by difficulty level
  const mathQuestions = {
    3: [ // 3 points level
      {
        id: 1,
        question: "What is 15 + 27?",
        options: ["42", "41", "43", "40"],
        correct: 0,
        subject: "Mathematics",
        difficulty: "Easy"
      },
      {
        id: 2,
        question: "What is 8 × 7?",
        options: ["54", "56", "58", "52"],
        correct: 1,
        subject: "Mathematics",
        difficulty: "Easy"
      },
      {
        id: 3,
        question: "What is 144 ÷ 12?",
        options: ["11", "12", "13", "14"],
        correct: 1,
        subject: "Mathematics",
        difficulty: "Easy"
      },
      {
        id: 4,
        question: "What is 25% of 80?",
        options: ["15", "20", "25", "30"],
        correct: 1,
        subject: "Mathematics",
        difficulty: "Easy"
      },
      {
        id: 5,
        question: "What is the perimeter of a rectangle with length 8 and width 5?",
        options: ["26", "24", "28", "22"],
        correct: 0,
        subject: "Mathematics",
        difficulty: "Easy"
      }
    ],
    4: [ // 4 points level
      {
        id: 6,
        question: "Solve for x: 3x + 7 = 22",
        options: ["x = 5", "x = 4", "x = 6", "x = 3"],
        correct: 0,
        subject: "Mathematics",
        difficulty: "Medium"
      },
      {
        id: 7,
        question: "What is the square root of 169?",
        options: ["12", "13", "14", "15"],
        correct: 1,
        subject: "Mathematics",
        difficulty: "Medium"
      },
      {
        id: 8,
        question: "If a triangle has angles of 60° and 80°, what is the third angle?",
        options: ["40°", "50°", "30°", "45°"],
        correct: 0,
        subject: "Mathematics",
        difficulty: "Medium"
      },
      {
        id: 9,
        question: "What is 2³ + 3²?",
        options: ["17", "15", "19", "13"],
        correct: 0,
        subject: "Mathematics",
        difficulty: "Medium"
      },
      {
        id: 10,
        question: "What is the area of a circle with radius 4? (Use π ≈ 3.14)",
        options: ["50.24", "48.56", "52.14", "46.82"],
        correct: 0,
        subject: "Mathematics",
        difficulty: "Medium"
      }
    ],
    5: [ // 5 points level
      {
        id: 11,
        question: "Solve the quadratic equation: x² - 5x + 6 = 0",
        options: ["x = 2, 3", "x = 1, 6", "x = 2, 4", "x = 1, 5"],
        correct: 0,
        subject: "Mathematics",
        difficulty: "Hard"
      },
      {
        id: 12,
        question: "What is the derivative of f(x) = 3x² + 2x - 1?",
        options: ["6x + 2", "6x - 2", "3x + 2", "6x + 1"],
        correct: 0,
        subject: "Mathematics",
        difficulty: "Hard"
      },
      {
        id: 13,
        question: "If log₂(x) = 5, what is x?",
        options: ["32", "25", "10", "16"],
        correct: 0,
        subject: "Mathematics",
        difficulty: "Hard"
      },
      {
        id: 14,
        question: "What is the sum of the infinite geometric series: 1 + 1/2 + 1/4 + 1/8 + ...?",
        options: ["2", "1.5", "3", "2.5"],
        correct: 0,
        subject: "Mathematics",
        difficulty: "Hard"
      },
      {
        id: 15,
        question: "Find the integral of ∫(2x + 3)dx",
        options: ["x² + 3x + C", "2x² + 3x + C", "x² + 3 + C", "2x + 3x + C"],
        correct: 0,
        subject: "Mathematics",
        difficulty: "Hard"
      }
    ]
  };

  const getQuestionsForLevel = () => {
    return mathQuestions[selectedLevel] || [];
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

  const handleLevelSelect = (level) => {
    setSelectedLevel(level);
    setShowLevelSelection(false);
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
    }
  };

  const handleAnswerChange = (questionId, answerIndex) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answerIndex
    }));
  };

  const handleNext = () => {
    const questions = getQuestionsForLevel();
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

  const handleTestComplete = () => {
    setTestCompleted(true);
    
    // Calculate results
    const questions = getQuestionsForLevel();
    let correct = 0;
    questions.forEach(q => {
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
      levelColor = '#3B82F6';
    }
    
    setTestResult({
      correct,
      total: questions.length,
      percentage: Math.round(percentage),
      level,
      levelColor,
      timeUsed: 1800 - timeLeft,
      selectedLevel: selectedLevel
    });

    // Save test result to localStorage for progress tracking
    const testResults = JSON.parse(localStorage.getItem('mathTestResults') || '[]');
    const newResult = {
      date: new Date().toISOString(),
      selectedLevel: selectedLevel,
      correct: correct,
      total: questions.length,
      percentage: Math.round(percentage),
      level: level,
      timeUsed: 1800 - timeLeft
    };
    testResults.push(newResult);
    localStorage.setItem('mathTestResults', JSON.stringify(testResults));
  };

  const renderLevelSelection = () => (
    <>
      <HeaderCard elevation={0}>
        <Typography variant="h3" fontWeight={800} mb={1}>
          Select Test Level
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, mb: 3 }}>
          Choose your math level to take an appropriate test
        </Typography>
      </HeaderCard>

      <Grid container spacing={3}>
        {[3, 4, 5].map((level) => (
          <Grid item xs={12} md={4} key={level}>
            <GlassCard sx={{ cursor: 'pointer', height: '200px' }} onClick={() => handleLevelSelect(level)}>
              <CardContent sx={{ p: 4, textAlign: 'center', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <Typography variant="h2" fontWeight={800} mb={2} sx={{ color: level === 3 ? '#10B981' : level === 4 ? '#F59E0B' : '#EF4444' }}>
                  {level}
                </Typography>
                <Typography variant="h6" fontWeight={700} mb={1}>
                  {level === 3 ? 'Basic Level' : level === 4 ? 'Intermediate Level' : 'Advanced Level'}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  {level === 3 ? 'Basic arithmetic, percentages, geometry' : 
                   level === 4 ? 'Algebra, trigonometry, advanced geometry' : 
                   'Calculus, logarithms, advanced mathematics'}
                </Typography>
              </CardContent>
            </GlassCard>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <ActionButton onClick={() => setShowLevelSelection(false)}>
          Back
        </ActionButton>
      </Box>
    </>
  );

  const renderWelcomeScreen = () => (
    <>
      <HeaderCard elevation={0}>
        <Typography variant="h3" fontWeight={800} mb={1}>
          Mathematics Level Test
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, mb: 3 }}>
          Assess your mathematics skills and track your progress
        </Typography>
        <Stack direction="row" spacing={2} justifyContent="center">
          <ActionButton startIcon={<PlayArrow />} onClick={handleStartTest}>
            Start Test
          </ActionButton>
          <ActionButton startIcon={<Psychology />}>
            Practice Mode
          </ActionButton>
        </Stack>
      </HeaderCard>

      <GlassCard>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h5" fontWeight={700} mb={3} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <QuestionAnswer />
            Test Information
          </Typography>
          
          <Stack spacing={3}>
            <Box>
              <Typography variant="h6" fontWeight={600} mb={1}>📝 Subject</Typography>
              <Typography variant="body1" sx={{ opacity: 0.9 }}>
                Mathematics only - covering arithmetic, algebra, geometry, and calculus based on selected level
              </Typography>
            </Box>
            
            <Box>
              <Typography variant="h6" fontWeight={600} mb={1}>⏰ Duration</Typography>
              <Typography variant="body1" sx={{ opacity: 0.9 }}>
                30 minutes (5 questions per level)
              </Typography>
            </Box>
            
            <Box>
              <Typography variant="h6" fontWeight={600} mb={1}>🎯 Levels Available</Typography>
              <Stack direction="row" spacing={2} flexWrap="wrap" mt={1}>
                <Chip label="Level 3: Basic Math" sx={{ bgcolor: '#10B981', color: 'white' }} />
                <Chip label="Level 4: Intermediate Math" sx={{ bgcolor: '#F59E0B', color: 'white' }} />
                <Chip label="Level 5: Advanced Math" sx={{ bgcolor: '#EF4444', color: 'white' }} />
              </Stack>
            </Box>
            
            <Box>
              <Typography variant="h6" fontWeight={600} mb={1}>📊 Scoring</Typography>
              <Stack direction="row" spacing={2} flexWrap="wrap" mt={1}>
                <Chip label="Advanced: 90%+" sx={{ bgcolor: '#10B981', color: 'white' }} />
                <Chip label="Intermediate: 70-89%" sx={{ bgcolor: '#F59E0B', color: 'white' }} />
                <Chip label="Elementary: 50-69%" sx={{ bgcolor: '#3B82F6', color: 'white' }} />
                <Chip label="Beginner: <50%" sx={{ bgcolor: '#EF4444', color: 'white' }} />
              </Stack>
            </Box>
          </Stack>
        </CardContent>
      </GlassCard>
    </>
  );

  const renderTest = () => {
    const questions = getQuestionsForLevel();
    const question = questions[currentQuestion];
    const progress = ((currentQuestion + 1) / questions.length) * 100;

    return (
      <>
        {/* Test Header */}
        <GlassCard>
          <CardContent sx={{ p: 3 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6" fontWeight={700}>
                Question {currentQuestion + 1} of {questions.length} - Level {selectedLevel}
              </Typography>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Chip 
                  icon={<Timer />}
                  label={formatTime(timeLeft)}
                  sx={{ bgcolor: timeLeft < 300 ? '#EF4444' : '#10B981', color: 'white', fontWeight: 600 }}
                />
                <Chip 
                  label={question.subject}
                  sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)', color: 'white' }}
                />
                <Chip 
                  label={question.difficulty}
                  sx={{ 
                    bgcolor: question.difficulty === 'Easy' ? '#10B981' : 
                            question.difficulty === 'Medium' ? '#F59E0B' : '#EF4444',
                    color: 'white'
                  }}
                />
                <ActionButton 
                  startIcon={<Stop />}
                  onClick={handleStopTest}
                  sx={{ 
                    minWidth: 'auto',
                    px: 2,
                    bgcolor: 'rgba(239, 68, 68, 0.8)',
                    '&:hover': {
                      bgcolor: 'rgba(239, 68, 68, 1)',
                    }
                  }}
                >
                  Stop
                </ActionButton>
              </Stack>
            </Stack>
            
            <LinearProgress 
              variant="determinate" 
              value={progress} 
              sx={{
                height: 8,
                borderRadius: 4,
                bgcolor: 'rgba(255, 255, 255, 0.2)',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 4,
                  bgcolor: '#10B981'
                }
              }}
            />
          </CardContent>
        </GlassCard>

        {/* Question */}
        <QuestionCard>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h5" fontWeight={600} mb={4} lineHeight={1.6}>
              {question.question}
            </Typography>
            
            <RadioGroup
              value={answers[question.id] || ''}
              onChange={(e) => handleAnswerChange(question.id, parseInt(e.target.value))}
            >
              {question.options.map((option, index) => (
                <FormControlLabel
                  key={index}
                  value={index}
                  control={<Radio sx={{ color: 'rgba(255, 255, 255, 0.7)', '&.Mui-checked': { color: '#10B981' } }} />}
                  label={
                    <Typography variant="body1" sx={{ fontSize: '1.1rem', py: 1 }}>
                      {option}
                    </Typography>
                  }
                  sx={{ 
                    py: 1, 
                    px: 2, 
                    mx: 0,
                    borderRadius: 2,
                    transition: 'all 0.2s',
                    '&:hover': {
                      bgcolor: 'rgba(255, 255, 255, 0.1)'
                    }
                  }}
                />
              ))}
            </RadioGroup>
          </CardContent>
        </QuestionCard>

        {/* Navigation */}
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <ActionButton 
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
            sx={{ opacity: currentQuestion === 0 ? 0.5 : 1 }}
          >
            Previous
          </ActionButton>
          
          <Typography variant="body2" color="rgba(255, 255, 255, 0.7)">
            {Object.keys(answers).length} of {questions.length} answered
          </Typography>
          
          <ActionButton 
            onClick={handleNext}
            disabled={answers[question.id] === undefined}
            sx={{ 
              opacity: answers[question.id] === undefined ? 0.5 : 1,
              bgcolor: currentQuestion === questions.length - 1 ? '#10B981' : undefined
            }}
          >
            {currentQuestion === questions.length - 1 ? 'Finish Test' : 'Next'}
          </ActionButton>
        </Stack>
      </>
    );
  };

  const renderResults = () => (
    <>
      <HeaderCard elevation={0}>
        <Typography variant="h3" fontWeight={800} mb={1} sx={{ display: 'flex', alignItems: 'center', gap: 2, justifyContent: 'center' }}>
          <EmojiEvents sx={{ fontSize: '3rem', color: '#FFD700' }} />
          Test Complete!
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9 }}>
          Here are your results for Level {testResult.selectedLevel}
        </Typography>
      </HeaderCard>

      <GlassCard>
        <CardContent sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h2" fontWeight={800} mb={2} sx={{ color: testResult.levelColor }}>
            {testResult.percentage}%
          </Typography>
          
          <Chip 
            label={`${testResult.level} Level`}
            sx={{ 
              fontSize: '1.2rem',
              fontWeight: 700,
              py: 3,
              px: 4,
              bgcolor: testResult.levelColor,
              color: 'white',
              mb: 4
            }}
          />
          
          <Stack direction="row" spacing={4} justifyContent="center" mb={4}>
            <Box textAlign="center">
              <Typography variant="h4" fontWeight={700} color="#10B981">
                {testResult.correct}
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.8 }}>
                Correct
              </Typography>
            </Box>
            <Box textAlign="center">
              <Typography variant="h4" fontWeight={700} color="#EF4444">
                {testResult.total - testResult.correct}
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.8 }}>
                Incorrect
              </Typography>
            </Box>
            <Box textAlign="center">
              <Typography variant="h4" fontWeight={700} color="#3B82F6">
                {Math.floor(testResult.timeUsed / 60)}m
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.8 }}>
                Time Used
              </Typography>
            </Box>
          </Stack>
          
          <Stack direction="row" spacing={2} justifyContent="center">
            <ActionButton startIcon={<Refresh />} onClick={handleStartTest}>
              Retake Test
            </ActionButton>
            <ActionButton startIcon={<TrendingUp />}>
              View Progress
            </ActionButton>
          </Stack>
        </CardContent>
      </GlassCard>

      <Alert 
        severity="info" 
        sx={{ 
          bgcolor: 'rgba(59, 130, 246, 0.1)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          color: 'white',
          '& .MuiAlert-icon': { color: '#3B82F6' }
        }}
      >
        Based on your results, we'll recommend math courses that match your {testResult.level.toLowerCase()} level to help you progress effectively.
      </Alert>
    </>
  );

  return (
    <StyledContainer maxWidth="md">
      {!testStarted && !testCompleted && !showLevelSelection && renderWelcomeScreen()}
      {showLevelSelection && renderLevelSelection()}
      {testStarted && !testCompleted && renderTest()}
      {testCompleted && renderResults()}
    </StyledContainer>
  );
};

export default LevelTest;
