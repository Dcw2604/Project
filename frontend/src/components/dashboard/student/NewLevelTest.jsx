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
  IconButton,
  TextField,
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
  Stop,
  School,
  Send,
  ChatBubbleOutline,
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
    subject: 'algorithms',
    total_questions: 8, // Updated to match our generation: Level 3=8, Level 4=6, Level 5=4
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
  
  // New state for interactive practice chat
  const [showPracticeChat, setShowPracticeChat] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

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
        console.log('Submit answer response:', data);
        console.log('Test config type:', testConfig.test_type);
        
        // For practice tests, enable interactive chat mode
        if (testConfig.test_type === 'practice_test') {
          console.log('Processing practice test response...');
          if (data.practice_mode && data.chat_enabled) {
            console.log('Enabling practice chat mode');
            // Initialize chat with system message based on correctness
            const systemMessage = {
              type: 'system',
              message: (data.feedback || '') + " " + (data.message || ''),
              timestamp: new Date(),
              isCorrect: data.is_correct
            };
            
            // Add a helpful follow-up message for better user experience
            const welcomeMessage = {
              type: 'tutor',
              message: data.is_correct 
                ? "🎉 Excellent work! I'm here to help you explore different solution methods or clarify any concepts. What would you like to know?"
                : "🤔 Let's work through this together! I can give you hints, explain concepts, or guide you step-by-step. What would you like help with?",
              timestamp: new Date()
            };
            
            setChatMessages([systemMessage, welcomeMessage]);
            setShowPracticeChat(true);
            setCurrentExplanation({
              is_correct: data.is_correct,
              chat_enabled: true,
              question_id: data.question_id,
              test_session_id: data.test_session_id,
              correct_answer: data.correct_answer,
              explanation: data.explanation
            });
          } else {
            console.log('Falling back to explanation mode');
            // Fallback to old explanation mode
            setCurrentExplanation({
              is_correct: data.is_correct,
              correct_answer: data.correct_answer,
              explanation: data.explanation,
              question_explanation: data.question_explanation
            });
            setShowExplanation(true);
          }
        } else {
          // For level tests, just show basic feedback
          setCurrentExplanation({
            is_correct: data.is_correct,
            message: data.message || 'Answer submitted.'
          });
          setShowExplanation(true);
        }
        
        return data;
      } else {
        const errorData = await response.json();
        console.error('Submit answer error:', errorData);
        alert(`Error submitting answer: ${errorData.error}`);
        return null;
      }
    } catch (error) {
      alert(`Error submitting answer: ${error.message}`);
      return null;
    }
  };

  const sendPracticeChat = async () => {
    if (!chatInput.trim()) return;
    
    const userMessage = {
      type: 'user',
      message: chatInput.trim(),
      timestamp: new Date()
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    setChatLoading(true);
    
    const currentQuestion = questions[currentQuestionIndex];
    
    console.log('Sending practice chat message:', {
      test_session_id: currentTest?.id,
      question_id: currentQuestion?.id,
      question: chatInput.trim(),
      testConfig: testConfig
    });
    
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch('http://127.0.0.1:8000/api/tests/practice_chat/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          test_session_id: currentTest.id,
          question_id: currentQuestion.id,
          question: chatInput.trim()
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Practice chat response:', data);
        
        const tutorMessage = {
          type: 'tutor',
          message: data.tutor_response,
          timestamp: new Date(),
          questionContext: data.question_context
        };
        
        setChatMessages(prev => [...prev, tutorMessage]);
      } else {
        const errorData = await response.json();
        console.error('Practice chat error:', errorData);
        const errorMessage = {
          type: 'error',
          message: `Error: ${errorData.error || 'Failed to get tutor response'}`,
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Practice chat network error:', error);
      const errorMessage = {
        type: 'error',
        message: `Chat error: ${error.message}`,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    }
    
    setChatInput('');
    setChatLoading(false);
  };

  const handlePracticeContinue = () => {
    setShowPracticeChat(false);
    setChatMessages([]);
    setCurrentExplanation(null);
    
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      handleCompleteTest();
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
    setShowPracticeChat(false);
    setChatMessages([]);
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
          🎯 Algorithm Assessment Center
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, maxWidth: 600, mx: 'auto' }}>
          Choose your test type and difficulty level to begin your algorithmic journey
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
                    onChange={(e) => {
                      const level = e.target.value;
                      const questionCounts = { '3': 8, '4': 6, '5': 4 };
                      setTestConfig({ 
                        ...testConfig, 
                        difficulty_level: level, 
                        total_questions: questionCounts[level], 
                        time_limit_minutes: level === '3' ? 15 : level === '4' ? 20 : 25 
                      });
                    }}
                    sx={{ 
                      color: 'white',
                      '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.3)' }
                    }}
                  >
                    <MenuItem value="3">Level 3 - Basic (8 questions, 15 min)</MenuItem>
                    <MenuItem value="4">Level 4 - Intermediate (6 questions, 20 min)</MenuItem>
                    <MenuItem value="5">Level 5 - Advanced (4 questions, 25 min)</MenuItem>
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
                Interactive practice with AI tutor chat! Ask questions, get hints, and learn step-by-step without revealing answers.
              </Typography>
              
              <Box mb={3}>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel sx={{ color: 'white' }}>Practice Level</InputLabel>
                  <Select
                    value={testConfig.difficulty_level}
                    onChange={(e) => {
                      const level = e.target.value;
                      const questionCounts = { '3': 8, '4': 6, '5': 4 };
                      setTestConfig({ 
                        ...testConfig, 
                        difficulty_level: level, 
                        total_questions: questionCounts[level], 
                        time_limit_minutes: null 
                      });
                    }}
                    sx={{ 
                      color: 'white',
                      '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.3)' }
                    }}
                  >
                    <MenuItem value="3">Level 3 - Basic (8 questions)</MenuItem>
                    <MenuItem value="4">Level 4 - Intermediate (6 questions)</MenuItem>
                    <MenuItem value="5">Level 5 - Advanced (4 questions)</MenuItem>
                  </Select>
                </FormControl>
                
                <Stack spacing={1}>
                  <Chip label={`${testConfig.total_questions} Questions`} color="primary" />
                  <Chip label="No Time Limit" color="success" />
                  <Chip label="AI Tutor Chat" color="info" />
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

        {/* Interactive Practice Chat Dialog */}
        <Dialog open={showPracticeChat} maxWidth="md" fullWidth>
          <DialogTitle sx={{ background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)', color: 'white', display: 'flex', alignItems: 'center', gap: 2 }}>
            <ChatBubbleOutline />
            Practice Helper Chat
            {currentExplanation?.is_correct && (
              <Chip 
                label="✅ Correct Answer!" 
                color="success" 
                size="small"
                sx={{ ml: 'auto' }}
              />
            )}
          </DialogTitle>
          <DialogContent sx={{ background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)', color: 'white', minHeight: '400px', display: 'flex', flexDirection: 'column' }}>
            
            {/* Current Question Display */}
            <Paper sx={{ p: 2, mb: 2, backgroundColor: 'rgba(255,255,255,0.1)' }}>
              <Typography variant="body2" sx={{ opacity: 0.8, mb: 1 }}>
                Current Question:
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                {questions[currentQuestionIndex]?.question_text}
              </Typography>
              {answers[questions[currentQuestionIndex]?.id] && (
                <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
                  Your answer: <strong>{answers[questions[currentQuestionIndex]?.id]}</strong>
                </Typography>
              )}
            </Paper>

            {/* Chat Messages */}
            <Box sx={{ flexGrow: 1, overflowY: 'auto', mb: 2, maxHeight: '300px' }}>
              {chatMessages.map((msg, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <Box sx={{ 
                    display: 'flex', 
                    justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start',
                    mb: 1
                  }}>
                    <Paper sx={{ 
                      p: 2, 
                      maxWidth: '80%',
                      backgroundColor: msg.type === 'user' 
                        ? 'rgba(59, 130, 246, 0.3)' 
                        : msg.type === 'tutor'
                        ? 'rgba(16, 185, 129, 0.3)'
                        : msg.type === 'system'
                        ? 'rgba(107, 114, 128, 0.3)'
                        : 'rgba(239, 68, 68, 0.3)',
                      borderRadius: msg.type === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px'
                    }}>
                      <Typography variant="body2" sx={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: 1, 
                        mb: 0.5, 
                        opacity: 0.8,
                        fontSize: '0.75rem'
                      }}>
                        {msg.type === 'user' && '👤 You'}
                        {msg.type === 'tutor' && '🤖 Tutor'}
                        {msg.type === 'system' && '💡 System'}
                        {msg.type === 'error' && '⚠️ Error'}
                        <span style={{ marginLeft: 'auto' }}>
                          {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </Typography>
                      <Typography variant="body1">
                        {msg.message}
                      </Typography>
                    </Paper>
                  </Box>
                </Box>
              ))}
              {chatLoading && (
                <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                  <Paper sx={{ 
                    p: 2, 
                    backgroundColor: 'rgba(16, 185, 129, 0.3)',
                    borderRadius: '16px 16px 16px 4px'
                  }}>
                    <Typography variant="body1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      🤖 Tutor is thinking...
                      <CircularProgress size={16} sx={{ color: 'white' }} />
                    </Typography>
                  </Paper>
                </Box>
              )}
            </Box>

            {/* Chat Input */}
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
              <TextField
                fullWidth
                multiline
                maxRows={3}
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask me anything about this problem... (e.g., 'Give me a hint', 'What's the first step?', 'Explain this concept')"
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendPracticeChat();
                  }
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'rgba(255,255,255,0.1)',
                    color: 'white',
                    '& fieldset': { borderColor: 'rgba(255,255,255,0.3)' },
                    '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.5)' },
                    '&.Mui-focused fieldset': { borderColor: '#10B981' }
                  },
                  '& .MuiInputBase-input::placeholder': { color: 'rgba(255,255,255,0.6)' }
                }}
              />
              <Button
                onClick={sendPracticeChat}
                disabled={!chatInput.trim() || chatLoading}
                variant="contained"
                sx={{ 
                  background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                  minWidth: '60px',
                  height: '56px'
                }}
              >
                <Send />
              </Button>
            </Box>

            {/* Helpful Prompts */}
            <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              <Typography variant="caption" sx={{ opacity: 0.7, width: '100%', mb: 1 }}>
                Quick suggestions:
              </Typography>
              {[
                'Give me a hint',
                'What\'s the first step?', 
                'Explain this concept',
                'Is my approach correct?',
                'Show me a similar example'
              ].map((suggestion) => (
                <Chip
                  key={suggestion}
                  label={suggestion}
                  size="small"
                  onClick={() => setChatInput(suggestion)}
                  sx={{ 
                    backgroundColor: 'rgba(255,255,255,0.1)', 
                    color: 'white',
                    '&:hover': { backgroundColor: 'rgba(255,255,255,0.2)' }
                  }}
                />
              ))}
            </Box>
          </DialogContent>
          <DialogActions sx={{ background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)', gap: 1 }}>
            <Button 
              onClick={handlePracticeContinue}
              variant="contained"
              sx={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}
            >
              {currentQuestionIndex < questions.length - 1 ? 'Continue to Next Question' : 'Finish Practice'}
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
