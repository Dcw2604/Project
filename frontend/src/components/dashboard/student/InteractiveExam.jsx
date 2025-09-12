import React, { useState, useEffect, useRef } from 'react';
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
  Grid,
  CircularProgress,
  IconButton
} from '@mui/material';
import { 
  PlayArrow, 
  Timer, 
  QuestionAnswer,
  TrendingUp,
  Refresh,
  EmojiEvents,
  Psychology,
  Stop,
  Send,
  HelpOutline
} from '@mui/icons-material';

const StyledContainer = styled(Container)(({ theme }) => ({
  height: 'calc(100vh - 80px)',
  paddingTop: '2rem',
  paddingBottom: '2rem',
  background: 'transparent',
  overflow: 'auto',
}));

const StyledCard = styled(Card)(({ theme }) => ({
  background: 'rgba(255, 255, 255, 0.95)',
  backdropFilter: 'blur(10px)',
  borderRadius: '16px',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  marginBottom: theme.spacing(3),
}));

const ChatContainer = styled(Paper)(({ theme }) => ({
  height: '400px',
  overflow: 'auto',
  padding: theme.spacing(2),
  backgroundColor: '#f8f9fa',
  border: '1px solid #e9ecef',
  borderRadius: '12px',
  marginBottom: theme.spacing(2),
}));

const MessageBubble = styled(Box)(({ theme, sender }) => ({
  maxWidth: '75%',
  padding: theme.spacing(1.5, 2),
  marginBottom: theme.spacing(1.5),
  borderRadius: '18px',
  wordWrap: 'break-word',
  alignSelf: sender === 'student' ? 'flex-end' : 'flex-start',
  backgroundColor: sender === 'student' ? '#007bff' : '#ffffff',
  color: sender === 'student' ? '#ffffff' : '#333333',
  border: sender === 'ai' ? '1px solid #e9ecef' : 'none',
  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
}));

const ChatInputContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1),
  alignItems: 'flex-end',
  padding: theme.spacing(1),
  backgroundColor: '#ffffff',
  borderRadius: '12px',
  border: '1px solid #e9ecef',
}));

const InteractiveExam = () => {
  const [examState, setExamState] = useState('not_started');
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [currentInput, setCurrentInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [examProgress, setExamProgress] = useState({
    current: 0,
    total: 10,
    percentage: 0
  });
  const [examInfo, setExamInfo] = useState({
    question_number: 0,
    attempts_left: 3,
    hints_available: 3,
    state: 'WAITING_FOR_START'
  });
  const [completionReport, setCompletionReport] = useState(null);
  const [error, setError] = useState('');

  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const startExam = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/exam/start/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setSessionId(data.session_id);
        setExamState('in_progress');
        setMessages([
          {
            sender: 'ai',
            content: data.first_question,
            timestamp: new Date()
          }
        ]);
        setExamProgress({
          current: 1,
          total: 10,
          percentage: 10
        });
        setExamInfo({
          question_number: 1,
          attempts_left: 3,
          hints_available: 3,
          state: 'WAITING_FOR_ANSWER'
        });
      } else {
        setError(data.error || 'Failed to start exam');
      }
    } catch (err) {
      setError('שגיאת רשת. אנא נסה שנית.');
      console.error('Error starting exam:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!currentInput.trim() || isLoading) return;
    
    const userMessage = currentInput.trim();
    setCurrentInput('');
    
    setMessages(prev => [...prev, {
      sender: 'student',
      content: userMessage,
      timestamp: new Date()
    }]);
    
    setIsLoading(true);
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/exam/chat/${sessionId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: userMessage })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setMessages(prev => [...prev, {
          sender: 'ai',
          content: data.ai_response,
          timestamp: new Date(),
          isCorrect: data.is_correct
        }]);
        
        if (data.progress) {
          setExamProgress(data.progress);
        }
        
        if (data.exam_state) {
          setExamInfo(data.exam_state);
        }
        
        if (data.session_completed) {
          setExamState('completed');
          if (data.completion_report) {
            setCompletionReport(data.completion_report);
          }
        }
        
      } else {
        setError(data.error || 'Failed to process response');
        setMessages(prev => [...prev, {
          sender: 'ai',
          content: `❌ שגיאה: ${data.error || 'Failed to process your response'}`,
          timestamp: new Date()
        }]);
      }
    } catch (err) {
      setError('שגיאת רשת. אנא נסה שנית.');
      setMessages(prev => [...prev, {
        sender: 'ai',
        content: '❌ שגיאת רשת. אנא נסה שנית.',
        timestamp: new Date()
      }]);
      console.error('Error sending message:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const requestHint = () => {
    setCurrentInput('hint');
    setTimeout(() => sendMessage(), 100);
  };

  const resetExam = () => {
    setExamState('not_started');
    setSessionId(null);
    setMessages([]);
    setCurrentInput('');
    setExamProgress({ current: 0, total: 10, percentage: 0 });
    setExamInfo({ question_number: 0, attempts_left: 3, hints_available: 3, state: 'WAITING_FOR_START' });
    setCompletionReport(null);
    setError('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (examState === 'not_started') {
    return (
      <StyledContainer maxWidth="lg">
        <StyledCard>
          <CardContent sx={{ textAlign: 'center', p: 4 }}>
            <Psychology sx={{ fontSize: 80, color: '#4f46e5', mb: 2 }} />
            <Typography variant="h3" gutterBottom sx={{ fontWeight: 'bold', color: '#1a1a1a' }}>
              מבחן רמה אינטראקטיבי
            </Typography>
            <Typography variant="h6" color="text.secondary" gutterBottom sx={{ mb: 4 }}>
              מבחן מבוסס צ'אט עם שאלות פתוחות המופעל על ידי בינה מלאכותית
            </Typography>
            
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} md={4}>
                <Card sx={{ p: 2, backgroundColor: '#f8f9ff' }}>
                  <QuestionAnswer sx={{ fontSize: 40, color: '#4f46e5', mb: 1 }} />
                  <Typography variant="h6" gutterBottom>10 שאלות</Typography>
                  <Typography variant="body2" color="text.secondary">
                    שאלות פתוחות מבוססות על המסמכים שהועלו
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card sx={{ p: 2, backgroundColor: '#f0fff4' }}>
                  <HelpOutline sx={{ fontSize: 40, color: '#10b981', mb: 1 }} />
                  <Typography variant="h6" gutterBottom>רמזים חכמים</Typography>
                  <Typography variant="body2" color="text.secondary">
                    עד 3 רמזים שנוצרו על ידי AI לכל שאלה
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card sx={{ p: 2, backgroundColor: '#fffbf0' }}>
                  <TrendingUp sx={{ fontSize: 40, color: '#f59e0b', mb: 1 }} />
                  <Typography variant="h6" gutterBottom>3 ניסיונות</Typography>
                  <Typography variant="body2" color="text.secondary">
                    ניסיונות מרובים לכל שאלה עם משוב
                  </Typography>
                </Card>
              </Grid>
            </Grid>

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <Button
              variant="contained"
              size="large"
              startIcon={<PlayArrow />}
              onClick={startExam}
              disabled={isLoading}
              sx={{
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
                backgroundColor: '#4f46e5',
                '&:hover': { backgroundColor: '#3730a3' }
              }}
            >
              {isLoading ? <CircularProgress size={24} color="inherit" /> : 'התחל מבחן אינטראקטיבי'}
            </Button>
          </CardContent>
        </StyledCard>
      </StyledContainer>
    );
  }

  if (examState === 'completed') {
    return (
      <StyledContainer maxWidth="lg">
        <StyledCard>
          <CardContent sx={{ textAlign: 'center', p: 4 }}>
            <EmojiEvents sx={{ fontSize: 80, color: '#10b981', mb: 2 }} />
            <Typography variant="h3" gutterBottom sx={{ fontWeight: 'bold', color: '#1a1a1a' }}>
              המבחן הושלם!
            </Typography>
            
            {completionReport && (
              <Box sx={{ mt: 4 }}>
                <Grid container spacing={3} sx={{ mb: 4 }}>
                  <Grid item xs={12} md={3}>
                    <Card sx={{ p: 2, backgroundColor: '#f0fff4' }}>
                      <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#10b981' }}>
                        {completionReport.score}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        ציון סופי
                      </Typography>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Card sx={{ p: 2, backgroundColor: '#f8f9ff' }}>
                      <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#4f46e5' }}>
                        {completionReport.percentage}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        אחוזים
                      </Typography>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Card sx={{ p: 2, backgroundColor: '#fffbf0' }}>
                      <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#f59e0b' }}>
                        {completionReport.total_time}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        זמן כולל
                      </Typography>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Card sx={{ p: 2, backgroundColor: '#fef2f2' }}>
                      <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#ef4444' }}>
                        {completionReport.questions_with_hints}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        השתמש ברמזים
                      </Typography>
                    </Card>
                  </Grid>
                </Grid>
              </Box>
            )}

            <Button
              variant="contained"
              size="large"
              startIcon={<Refresh />}
              onClick={resetExam}
              sx={{
                mt: 3,
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
                backgroundColor: '#4f46e5',
                '&:hover': { backgroundColor: '#3730a3' }
              }}
            >
              עבור מבחן נוסף
            </Button>
          </CardContent>
        </StyledCard>
      </StyledContainer>
    );
  }

  // מבחן בתהליך
  return (
    <StyledContainer maxWidth="lg">
      <StyledCard>
        <CardContent>
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                מבחן אינטראקטיבי
              </Typography>
              <Button
                variant="outlined"
                startIcon={<Stop />}
                onClick={resetExam}
                size="small"
                color="error"
              >
                עצור מבחן
              </Button>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <Chip 
                icon={<QuestionAnswer />} 
                label={`שאלה ${examProgress.current}/${examProgress.total}`} 
                color="primary" 
              />
              <Chip 
                icon={<Timer />} 
                label={`${examInfo.attempts_left} ניסיונות נותרו`} 
                color={examInfo.attempts_left <= 1 ? 'error' : 'default'} 
              />
              <Chip 
                icon={<HelpOutline />} 
                label={`${examInfo.hints_available} רמזים זמינים`} 
                color={examInfo.hints_available === 0 ? 'error' : 'success'} 
              />
            </Box>
            
            <LinearProgress 
              variant="determinate" 
              value={examProgress.percentage} 
              sx={{ height: 8, borderRadius: 4 }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
              {examProgress.percentage}% הושלם
            </Typography>
          </Box>

          <ChatContainer ref={chatContainerRef}>
            <Stack spacing={1}>
              {messages.map((message, index) => (
                <Box key={index} sx={{ display: 'flex', justifyContent: message.sender === 'student' ? 'flex-end' : 'flex-start' }}>
                  <MessageBubble sender={message.sender}>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {message.content}
                    </Typography>
                    {message.isCorrect !== undefined && (
                      <Chip 
                        size="small" 
                        label={message.isCorrect ? 'נכון!' : 'לא נכון'} 
                        color={message.isCorrect ? 'success' : 'error'}
                        sx={{ mt: 1 }}
                      />
                    )}
                  </MessageBubble>
                </Box>
              ))}
              {isLoading && (
                <Box sx={{ display: 'flex', justifyContent: 'flex-start' }}>
                  <MessageBubble sender="ai">
                    <CircularProgress size={20} />
                    <Typography variant="body2" sx={{ ml: 1 }}>
                      מעבד את התשובה שלך...
                    </Typography>
                  </MessageBubble>
                </Box>
              )}
            </Stack>
          </ChatContainer>

          <ChatInputContainer>
            <TextField
              fullWidth
              multiline
              maxRows={3}
              placeholder="הקלד את התשובה כאן..."
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
              variant="outlined"
              size="small"
            />
            <IconButton 
              onClick={requestHint} 
              disabled={isLoading || examInfo.hints_available === 0}
              color="primary"
              title="בקש רמז"
            >
              <HelpOutline />
            </IconButton>
            <IconButton 
              onClick={sendMessage} 
              disabled={isLoading || !currentInput.trim()}
              color="primary"
              title="שלח תשובה"
            >
              <Send />
            </IconButton>
          </ChatInputContainer>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </CardContent>
      </StyledCard>
    </StyledContainer>
  );
};

export default InteractiveExam;
