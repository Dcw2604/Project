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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  IconButton
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
  Stop,
  School,
  Assignment,
  QuestionMark,
  LightbulbOutlined
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
  background: 'rgba(255, 255, 255, 0.1)',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  borderRadius: '20px',
  color: 'white',
  marginBottom: theme.spacing(3),
}));

const NewLevelTest = () => {
  const [currentView, setCurrentView] = useState('menu'); // menu, test, results, practice
  const [testConfig, setTestConfig] = useState({
    test_type: 'level_test',
    difficulty_level: '3',
    subject: 'math',
    total_questions: 10,
    time_limit_minutes: null
  });
  
  const [currentTest, setCurrentTest] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(null);
  const [testStartTime, setTestStartTime] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [currentExplanation, setCurrentExplanation] = useState(null);

  useEffect(() => {
    if (timeLeft !== null && timeLeft > 0 && currentView === 'test') {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0) {
      handleCompleteTest();
    }
  }, [timeLeft, currentView]);

  const startTest = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch('http://127.0.0.1:8000/api/tests/start/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testConfig),
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentTest(data.test_session);
        setQuestions(data.questions);
        setCurrentQuestionIndex(0);
        setAnswers({});
        setTestStartTime(Date.now());
        
        if (testConfig.test_type === 'level_test' && testConfig.time_limit_minutes) {
          setTimeLeft(testConfig.time_limit_minutes * 60);
        } else {
          setTimeLeft(null);
        }
        
        setCurrentView('test');
      } else {
        const errorData = await response.json();
        alert(`Failed to start test: ${errorData.error}`);
      }
    } catch (error) {
      alert(`Error starting test: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async (questionId, answer) => {
    const timeTaken = testStartTime ? Math.floor((Date.now() - testStartTime) / 1000) : null;
    
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch('http://127.0.0.1:8000/api/tests/submit_answer/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          test_session_id: currentTest.id,
          question_id: questionId,
          answer: answer,
          time_taken_seconds: timeTaken
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // For practice tests, show explanation immediately
        if (testConfig.test_type === 'practice_test') {
          setCurrentExplanation({
            is_correct: data.is_correct,
            correct_answer: data.correct_answer,
            explanation: data.explanation,
            question_explanation: data.question_explanation
          });
          setShowExplanation(true);
        }
        
        return data;
      } else {
        const errorData = await response.json();
        alert(`Error submitting answer: ${errorData.error}`);
        return null;
      }
    } catch (error) {
      alert(`Error submitting answer: ${error.message}`);
      return null;
    }
  };

  const handleAnswerSelect = async (answer) => {
    const currentQuestion = questions[currentQuestionIndex];
    setAnswers({ ...answers, [currentQuestion.id]: answer });
    
    // Submit answer to backend
    await submitAnswer(currentQuestion.id, answer);
    
    // For practice tests, wait for user to continue after seeing explanation
    if (testConfig.test_type !== 'practice_test') {
      // Auto-advance for level tests
      setTimeout(() => {
        if (currentQuestionIndex < questions.length - 1) {
          setCurrentQuestionIndex(currentQuestionIndex + 1);
        } else {
          handleCompleteTest();
        }
      }, 1000);
    }
  };

  const handleNextQuestion = () => {
    setShowExplanation(false);
    setCurrentExplanation(null);
    
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      handleCompleteTest();
    }
  };

  const handleCompleteTest = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch('http://127.0.0.1:8000/api/tests/complete/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          test_session_id: currentTest.id
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data);
        setCurrentView('results');
      } else {
        const errorData = await response.json();
        alert(`Error completing test: ${errorData.error}`);
      }
    } catch (error) {
      alert(`Error completing test: ${error.message}`);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const renderMenu = () => (
    <StyledContainer maxWidth="lg">
      <Box textAlign="center" mb={6}>
        <Typography variant="h2" fontWeight={800} mb={2} sx={{
          background: 'linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          🎯 Math Assessment Center
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, maxWidth: 600, mx: 'auto' }}>
          Choose your test type and difficulty level to begin your mathematical journey
        </Typography>
      </Box>

      <Grid container spacing={4} justifyContent="center">
        {/* Level Test Card */}
        <Grid item xs={12} md={6}>
          <GlassCard>
            <CardContent sx={{ p: 4, textAlign: 'center' }}>
              <EmojiEvents sx={{ fontSize: 60, color: '#F59E0B', mb: 2 }} />
              <Typography variant="h4" fontWeight={700} mb={2}>
                📊 Level Test
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.9, mb: 3 }}>
                Official assessment with time limits. Pass to unlock the next level and earn points!
              </Typography>
              
              <Box mb={3}>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel sx={{ color: 'white' }}>Difficulty Level</InputLabel>
                  <Select
                    value={testConfig.difficulty_level}
                    onChange={(e) => setTestConfig({ ...testConfig, difficulty_level: e.target.value, time_limit_minutes: e.target.value === '3' ? 15 : e.target.value === '4' ? 20 : 25 })}
                    sx={{ 
                      color: 'white',
                      '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.3)' }
                    }}
                  >
                    <MenuItem value="3">Level 3 - Basic (15 min)</MenuItem>
                    <MenuItem value="4">Level 4 - Intermediate (20 min)</MenuItem>
                    <MenuItem value="5">Level 5 - Advanced (25 min)</MenuItem>
                  </Select>
                </FormControl>
                
                <Stack spacing={1}>
                  <Chip label={`${testConfig.total_questions} Questions`} color="primary" />
                  <Chip label={`${testConfig.time_limit_minutes || 15} Minutes`} color="warning" />
                  <Chip label="70% to Pass" color="success" />
                </Stack>
              </Box>

              <Button
                variant="contained"
                size="large"
                startIcon={<PlayArrow />}
                onClick={() => {
                  setTestConfig({ ...testConfig, test_type: 'level_test' });
                  startTest();
                }}
                disabled={loading}
                sx={{
                  background: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
                  borderRadius: '12px',
                  py: 1.5,
                  px: 4,
                  fontWeight: 600,
                  fontSize: '1.1rem'
                }}
              >
                {loading ? 'Starting...' : 'Start Level Test'}
              </Button>
            </CardContent>
          </GlassCard>
        </Grid>

        {/* Practice Test Card */}
        <Grid item xs={12} md={6}>
          <GlassCard>
            <CardContent sx={{ p: 4, textAlign: 'center' }}>
              <Psychology sx={{ fontSize: 60, color: '#10B981', mb: 2 }} />
              <Typography variant="h4" fontWeight={700} mb={2}>
                🧠 Practice Mode
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.9, mb: 3 }}>
                Practice without time pressure. Get instant explanations for each question!
              </Typography>
              
              <Box mb={3}>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel sx={{ color: 'white' }}>Practice Level</InputLabel>
                  <Select
                    value={testConfig.difficulty_level}
                    onChange={(e) => setTestConfig({ ...testConfig, difficulty_level: e.target.value, time_limit_minutes: null })}
                    sx={{ 
                      color: 'white',
                      '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.3)' }
                    }}
                  >
                    <MenuItem value="3">Level 3 - Basic</MenuItem>
                    <MenuItem value="4">Level 4 - Intermediate</MenuItem>
                    <MenuItem value="5">Level 5 - Advanced</MenuItem>
                  </Select>
                </FormControl>
                
                <Stack spacing={1}>
                  <Chip label={`${testConfig.total_questions} Questions`} color="primary" />
                  <Chip label="No Time Limit" color="success" />
                  <Chip label="Instant Feedback" color="info" />
                </Stack>
              </Box>

              <Button
                variant="contained"
                size="large"
                startIcon={<Psychology />}
                onClick={() => {
                  setTestConfig({ ...testConfig, test_type: 'practice_test', time_limit_minutes: null });
                  startTest();
                }}
                disabled={loading}
                sx={{
                  background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                  borderRadius: '12px',
                  py: 1.5,
                  px: 4,
                  fontWeight: 600,
                  fontSize: '1.1rem'
                }}
              >
                {loading ? 'Starting...' : 'Start Practice'}
              </Button>
            </CardContent>
          </GlassCard>
        </Grid>
      </Grid>
    </StyledContainer>
  );

  const renderTest = () => {
    const currentQuestion = questions[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

    return (
      <StyledContainer maxWidth="md">
        {/* Header */}
        <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
          <Typography variant="h5" fontWeight={600}>
            {testConfig.test_type === 'level_test' ? '📊 Level Test' : '🧠 Practice Mode'}
            {' - Level '}{testConfig.difficulty_level}
          </Typography>
          {timeLeft !== null && (
            <Chip 
              icon={<Timer />} 
              label={formatTime(timeLeft)}
              color={timeLeft < 300 ? 'error' : 'primary'}
              sx={{ fontWeight: 600, fontSize: '1rem' }}
            />
          )}
        </Box>

        {/* Progress */}
        <Box mb={4}>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2">Question {currentQuestionIndex + 1} of {questions.length}</Typography>
            <Typography variant="body2">{Math.round(progress)}% Complete</Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: 'rgba(255,255,255,0.2)',
              '& .MuiLinearProgress-bar': {
                background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                borderRadius: 4,
              }
            }}
          />
        </Box>

        {/* Question */}
        <GlassCard>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h6" fontWeight={600} mb={3}>
              {currentQuestion?.question_text}
            </Typography>

            <RadioGroup
              value={answers[currentQuestion?.id] || ''}
              onChange={(e) => handleAnswerSelect(e.target.value)}
            >
              {currentQuestion?.option_a && (
                <FormControlLabel 
                  value="A" 
                  control={<Radio sx={{ color: 'white' }} />} 
                  label={`A. ${currentQuestion.option_a}`}
                  sx={{ mb: 1, color: 'white' }}
                />
              )}
              {currentQuestion?.option_b && (
                <FormControlLabel 
                  value="B" 
                  control={<Radio sx={{ color: 'white' }} />} 
                  label={`B. ${currentQuestion.option_b}`}
                  sx={{ mb: 1, color: 'white' }}
                />
              )}
              {currentQuestion?.option_c && (
                <FormControlLabel 
                  value="C" 
                  control={<Radio sx={{ color: 'white' }} />} 
                  label={`C. ${currentQuestion.option_c}`}
                  sx={{ mb: 1, color: 'white' }}
                />
              )}
              {currentQuestion?.option_d && (
                <FormControlLabel 
                  value="D" 
                  control={<Radio sx={{ color: 'white' }} />} 
                  label={`D. ${currentQuestion.option_d}`}
                  sx={{ mb: 1, color: 'white' }}
                />
              )}
            </RadioGroup>
          </CardContent>
        </GlassCard>

        {/* Explanation Dialog for Practice Mode */}
        <Dialog open={showExplanation} maxWidth="md" fullWidth>
          <DialogTitle sx={{ background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)', color: 'white' }}>
            {currentExplanation?.is_correct ? '✅ Correct!' : '❌ Incorrect'}
          </DialogTitle>
          <DialogContent sx={{ background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)', color: 'white' }}>
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                Correct Answer: {currentExplanation?.correct_answer}
              </Typography>
              <Divider sx={{ my: 2, borderColor: 'rgba(255,255,255,0.2)' }} />
              <Typography variant="body1" paragraph>
                <strong>Explanation:</strong>
              </Typography>
              <Typography variant="body1" paragraph>
                {currentExplanation?.explanation || currentExplanation?.question_explanation || 'No explanation available.'}
              </Typography>
            </Box>
          </DialogContent>
          <DialogActions sx={{ background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)' }}>
            <Button 
              onClick={handleNextQuestion}
              variant="contained"
              sx={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}
            >
              {currentQuestionIndex < questions.length - 1 ? 'Next Question' : 'Finish Test'}
            </Button>
          </DialogActions>
        </Dialog>
      </StyledContainer>
    );
  };

  const renderResults = () => (
    <StyledContainer maxWidth="md">
      <Box textAlign="center" mb={4}>
        <Typography variant="h3" fontWeight={800} mb={2} sx={{
          background: 'linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          {results?.passed ? '🎉 Congratulations!' : '📚 Keep Learning!'}
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9 }}>
          {testConfig.test_type === 'level_test' ? 'Level Test' : 'Practice Test'} Results
        </Typography>
      </Box>

      <GlassCard>
        <CardContent sx={{ p: 4 }}>
          <Grid container spacing={3} textAlign="center">
            <Grid item xs={12} md={3}>
              <Typography variant="h3" fontWeight={700} color={results?.passed ? '#10B981' : '#EF4444'}>
                {Math.round(results?.score || 0)}%
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>Final Score</Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="h3" fontWeight={700} color="#10B981">
                {results?.correct_answers || 0}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>Correct</Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="h3" fontWeight={700} color="#EF4444">
                {(results?.total_questions || 0) - (results?.correct_answers || 0)}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>Incorrect</Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="h3" fontWeight={700} color="#F59E0B">
                {results?.points_earned || 0}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>Points</Typography>
            </Grid>
          </Grid>

          <Divider sx={{ my: 3, borderColor: 'rgba(255,255,255,0.2)' }} />

          {results?.passed ? (
            <Alert severity="success" sx={{ mb: 3 }}>
              <Typography variant="h6">🎯 Level Passed!</Typography>
              <Typography>You've successfully completed Level {testConfig.difficulty_level}. Keep up the great work!</Typography>
            </Alert>
          ) : (
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="h6">📚 Keep Practicing!</Typography>
              <Typography>You need 70% to pass. Review the material and try again when you're ready.</Typography>
            </Alert>
          )}

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center">
            <Button
              variant="contained"
              startIcon={<Refresh />}
              onClick={() => setCurrentView('menu')}
              sx={{
                background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                borderRadius: '12px',
                py: 1.5,
                px: 4
              }}
            >
              Take Another Test
            </Button>
            {!results?.passed && testConfig.test_type === 'level_test' && (
              <Button
                variant="outlined"
                startIcon={<Psychology />}
                onClick={() => {
                  setTestConfig({ ...testConfig, test_type: 'practice_test', time_limit_minutes: null });
                  setCurrentView('menu');
                }}
                sx={{ borderColor: 'white', color: 'white', py: 1.5, px: 4 }}
              >
                Practice This Level
              </Button>
            )}
          </Stack>
        </CardContent>
      </GlassCard>
    </StyledContainer>
  );

  return (
    <Box sx={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
      py: 2
    }}>
      {currentView === 'menu' && renderMenu()}
      {currentView === 'test' && renderTest()}
      {currentView === 'results' && renderResults()}
    </Box>
  );
};

export default NewLevelTest;
