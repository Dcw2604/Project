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
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import { 
  PlayArrow, 
  CheckCircle, 
  Timer, 
  QuestionAnswer,
  TrendingUp,
  Refresh,
  EmojiEvents,
  Psychology
} from '@mui/icons-material';

const StyledContainer = styled(Container)(({ theme }) => ({
  height: 'calc(100vh - 80px)', // Account for header height
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

  const questions = [
    {
      id: 1,
      question: "What is the primary purpose of photosynthesis in plants?",
      options: [
        "To produce oxygen for animals",
        "To convert light energy into chemical energy",
        "To absorb water from soil",
        "To reproduce and create seeds"
      ],
      correct: 1,
      subject: "Science",
      difficulty: "Easy"
    },
    {
      id: 2,
      question: "Which of the following is NOT a prime number?",
      options: ["17", "19", "21", "23"],
      correct: 2,
      subject: "Mathematics",
      difficulty: "Medium"
    },
    {
      id: 3,
      question: "In Shakespeare's 'Romeo and Juliet', what are the names of the feuding families?",
      options: [
        "Montague and Capulet",
        "Benvolio and Tybalt",
        "Verona and Mantua",
        "Mercutio and Paris"
      ],
      correct: 0,
      subject: "Literature",
      difficulty: "Medium"
    },
    {
      id: 4,
      question: "What is the chemical formula for water?",
      options: ["CO2", "H2O", "O2", "NaCl"],
      correct: 1,
      subject: "Chemistry",
      difficulty: "Easy"
    },
    {
      id: 5,
      question: "Which historical event marked the beginning of World War II?",
      options: [
        "Attack on Pearl Harbor",
        "Invasion of Poland",
        "Battle of Britain",
        "Fall of France"
      ],
      correct: 1,
      subject: "History",
      difficulty: "Hard"
    }
  ];

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

  const handleStartTest = () => {
    setTestStarted(true);
    setCurrentQuestion(0);
    setAnswers({});
    setTestCompleted(false);
    setTimeLeft(1800);
    setTestResult(null);
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

  const handleTestComplete = () => {
    setTestCompleted(true);
    
    // Calculate results
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
      timeUsed: 1800 - timeLeft
    });
  };

  const renderWelcomeScreen = () => (
    <>
      <HeaderCard elevation={0}>
        <Typography variant="h3" fontWeight={800} mb={1}>
          Level Assessment Test
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, mb: 3 }}>
          Discover your academic level across multiple subjects
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
              <Typography variant="h6" fontWeight={600} mb={1}>📝 Format</Typography>
              <Typography variant="body1" sx={{ opacity: 0.9 }}>
                Multiple choice questions covering Mathematics, Science, Literature, and History
              </Typography>
            </Box>
            
            <Box>
              <Typography variant="h6" fontWeight={600} mb={1}>⏰ Duration</Typography>
              <Typography variant="body1" sx={{ opacity: 0.9 }}>
                30 minutes ({questions.length} questions)
              </Typography>
            </Box>
            
            <Box>
              <Typography variant="h6" fontWeight={600} mb={1}>🎯 Purpose</Typography>
              <Typography variant="body1" sx={{ opacity: 0.9 }}>
                Determine your current academic level to recommend appropriate courses
              </Typography>
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
    const question = questions[currentQuestion];
    const progress = ((currentQuestion + 1) / questions.length) * 100;

    return (
      <>
        {/* Test Header */}
        <GlassCard>
          <CardContent sx={{ p: 3 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6" fontWeight={700}>
                Question {currentQuestion + 1} of {questions.length}
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
                  bgcolor: '#10B981'
                }
              }} 
            />
          </CardContent>
        </GlassCard>

        {/* Question */}
        <QuestionCard>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h5" fontWeight={600} mb={4}>
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
          Here are your results
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
              View Recommendations
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
        Based on your results, we'll recommend courses that match your {testResult.level.toLowerCase()} level to help you progress effectively.
      </Alert>
    </>
  );

  return (
    <StyledContainer maxWidth="md">
      {!testStarted && !testCompleted && renderWelcomeScreen()}
      {testStarted && !testCompleted && renderTest()}
      {testCompleted && renderResults()}
    </StyledContainer>
  );
};

export default LevelTest;
