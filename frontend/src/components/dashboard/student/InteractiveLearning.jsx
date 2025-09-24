import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Card,
  CardContent,
  Chip,
  Avatar,
  LinearProgress,
  Divider,
  Alert,
  CircularProgress,
  Grid,
  Fade,
  Zoom
} from '@mui/material';
import {
  Psychology,
  Chat,
  TrendingUp,
  LightbulbOutlined,
  QuestionAnswer,
  CheckCircle,
  School,
  SendRounded
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { useAuth } from '../../../hooks/useAuth';

// Styled components for glass effect
const GlassCard = styled(Paper)(({ theme }) => ({
  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05))',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  borderRadius: '20px',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
}));

const ChatBubble = styled(Box)(({ theme, isai }) => ({
  maxWidth: '80%',
  padding: '16px 20px',
  borderRadius: '20px',
  marginBottom: '16px',
  background: isai 
    ? 'linear-gradient(135deg, rgba(33, 150, 243, 0.2), rgba(33, 150, 243, 0.1))'
    : 'linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(76, 175, 80, 0.1))',
  border: `1px solid ${isai ? 'rgba(33, 150, 243, 0.3)' : 'rgba(76, 175, 80, 0.3)'}`,
  backdropFilter: 'blur(10px)',
  boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
  alignSelf: isai ? 'flex-start' : 'flex-end',
  position: 'relative',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: '10px',
    [isai ? 'left' : 'right']: '-6px',
    width: 0,
    height: 0,
    border: `6px solid transparent`,
    borderTopColor: isai ? 'rgba(33, 150, 243, 0.2)' : 'rgba(76, 175, 80, 0.2)',
  }
}));

const TopicCard = styled(Card)(({ theme, selected }) => ({
  background: selected 
    ? 'linear-gradient(135deg, rgba(33, 150, 243, 0.3), rgba(33, 150, 243, 0.1))'
    : 'linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05))',
  backdropFilter: 'blur(20px)',
  border: `2px solid ${selected ? 'rgba(33, 150, 243, 0.5)' : 'rgba(255, 255, 255, 0.2)'}`,
  borderRadius: '16px',
  cursor: 'pointer',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: '0 12px 32px rgba(0, 0, 0, 0.15)',
    border: '2px solid rgba(33, 150, 243, 0.4)',
  }
}));

const InteractiveLearning = () => {
  const [sessionId, setSessionId] = useState(null);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionData, setSessionData] = useState(null);
  const [progress, setProgress] = useState({
    understanding_level: 0,
    engagement_score: 0,
    discoveries_made: 0
  });
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [showTopicSelector, setShowTopicSelector] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [questionHistory, setQuestionHistory] = useState([]);
  const [showNextQuestion, setShowNextQuestion] = useState(false);
  const [error, setError] = useState(null);
  
  const { user } = useAuth();

  const topics = [
    {
      id: 'algebraic-equations',
      title: 'Algebraic Equations',
      description: 'Discover how to solve for unknown values',
      icon: '🔢',
      subject: 'math',
      goal: 'Understand how to solve for x in basic equations through discovery'
    },
    {
      id: 'fractions',
      title: 'Fractions',
      description: 'Explore parts of a whole',
      icon: '🍕',
      subject: 'math',
      goal: 'Master fraction operations through visual understanding'
    },
    {
      id: 'geometry-basics',
      title: 'Geometry Basics',
      description: 'Understand shapes and their properties',
      icon: '📐',
      subject: 'math',
      goal: 'Discover geometric relationships through exploration'
    },
    {
      id: 'probability',
      title: 'Probability',
      description: 'Learn about chance and likelihood',
      icon: '🎲',
      subject: 'math',
      goal: 'Understand probability through real-world scenarios'
    }
  ];

  const startLearningSession = async (topic) => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch('http://127.0.0.1:8000/api/interactive/start/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`
        },
        body: JSON.stringify({
          topic: topic.title,
          subject: topic.subject,
          learning_goal: topic.goal,
          session_type: 'interactive_learning'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        setSessionData(data);
        setIsSessionActive(true);
        setShowTopicSelector(false);
        setCurrentQuestion(data.initial_question);
        
        // Add welcome message and initial question
        setMessages([
          {
            content: data.welcome_message,
            sender: 'ai',
            timestamp: new Date().toLocaleTimeString()
          },
          {
            content: data.initial_question,
            sender: 'ai',
            timestamp: new Date().toLocaleTimeString(),
            isQuestion: true
          }
        ]);
      } else {
        throw new Error('Failed to start session');
      }
    } catch (error) {
      setError('Failed to start learning session. Please try again.');
      console.error('Error starting session:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || !sessionId) return;

    const userMessage = {
      content: currentMessage,
      sender: 'student',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setLoading(true);

    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`http://127.0.0.1:8000/api/interactive/chat/${sessionId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`
        },
        body: JSON.stringify({
          message: currentMessage
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        const aiMessage = {
          content: data.ai_response,
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString(),
          understanding_level: data.understanding_level,
          discovery_detected: data.discovery_detected,
          hint_level: data.hint_level
        };

        setMessages(prev => [...prev, aiMessage]);
        
        // Update current question if there's a next question
        if (data.next_question) {
          setCurrentQuestion(data.next_question);
          setShowNextQuestion(true);
        }
        
        // Check if session is complete
        if (data.session_complete) {
          if (data.next_question) {
            // Show completion with next challenge option
            setTimeout(() => {
              setShowNextQuestion(true);
            }, 2000);
          } else {
            await endSession();
          }
        } else {
          // Update progress
          await fetchProgress();
        }
      } else {
        throw new Error('Failed to send message');
      }
    } catch (error) {
      setError('Failed to send message. Please try again.');
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProgress = async () => {
    if (!sessionId) return;

    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`http://127.0.0.1:8000/api/interactive/progress/${sessionId}/`, {
        method: 'GET',
        headers: {
          'Authorization': `Token ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProgress({
          understanding_level: data.understanding_level,
          engagement_score: data.engagement_score,
          discoveries_made: data.discoveries_made,
          confusion_indicators: data.confusion_indicators,
          breakthrough_moments: data.breakthrough_moments
        });
      }
    } catch (error) {
      console.error('Error fetching progress:', error);
    }
  };

  const endSession = async () => {
    if (!sessionId) return;

    try {
      const token = localStorage.getItem('authToken');
      await fetch(`http://127.0.0.1:8000/api/interactive/end/${sessionId}/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`
        }
      });

      setIsSessionActive(false);
      setShowTopicSelector(true);
      setSessionId(null);
      setMessages([]);
      setProgress({ understanding_level: 0, engagement_score: 0, discoveries_made: 0 });
    } catch (error) {
      console.error('Error ending session:', error);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  useEffect(() => {
    if (sessionId) {
      const interval = setInterval(fetchProgress, 10000); // Update progress every 10 seconds
      return () => clearInterval(interval);
    }
  }, [sessionId]);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography 
          variant="h3" 
          sx={{ 
            fontWeight: 800, 
            color: 'white',
            textShadow: '0 2px 20px rgba(0,0,0,0.3)',
            mb: 2
          }}
        >
          🧠 Interactive Learning
        </Typography>
        <Typography 
          variant="h6" 
          sx={{ 
            color: 'rgba(255, 255, 255, 0.8)',
            fontWeight: 400
          }}
        >
          Discover knowledge through conversation - no direct answers, just guided exploration!
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>
          {error}
        </Alert>
      )}

      {/* Topic Selector */}
      {showTopicSelector && (
        <Fade in={showTopicSelector}>
          <Box>
            <Typography 
              variant="h5" 
              sx={{ 
                color: 'white', 
                mb: 3, 
                textAlign: 'center',
                fontWeight: 600
              }}
            >
              Choose Your Learning Adventure
            </Typography>
            
            <Grid container spacing={3}>
              {topics.map((topic) => (
                <Grid item xs={12} md={6} key={topic.id}>
                  <TopicCard 
                    selected={selectedTopic?.id === topic.id}
                    onClick={() => setSelectedTopic(topic)}
                  >
                    <CardContent sx={{ p: 3 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Typography sx={{ fontSize: '2rem', mr: 2 }}>
                          {topic.icon}
                        </Typography>
                        <Typography 
                          variant="h6" 
                          sx={{ 
                            color: 'white', 
                            fontWeight: 700 
                          }}
                        >
                          {topic.title}
                        </Typography>
                      </Box>
                      <Typography 
                        sx={{ 
                          color: 'rgba(255, 255, 255, 0.8)', 
                          mb: 2 
                        }}
                      >
                        {topic.description}
                      </Typography>
                      <Typography 
                        variant="caption" 
                        sx={{ 
                          color: 'rgba(255, 255, 255, 0.6)',
                          fontStyle: 'italic'
                        }}
                      >
                        Goal: {topic.goal}
                      </Typography>
                    </CardContent>
                  </TopicCard>
                </Grid>
              ))}
            </Grid>

            {selectedTopic && (
              <Zoom in={Boolean(selectedTopic)}>
                <Box sx={{ textAlign: 'center', mt: 4 }}>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={() => startLearningSession(selectedTopic)}
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={20} /> : <Psychology />}
                    sx={{
                      borderRadius: '16px',
                      px: 4,
                      py: 2,
                      fontSize: '1.1rem',
                      fontWeight: 700,
                      background: 'linear-gradient(135deg, #2196F3, #1976D2)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #1976D2, #1565C0)',
                        transform: 'translateY(-2px)',
                      }
                    }}
                  >
                    Start Learning Journey
                  </Button>
                </Box>
              </Zoom>
            )}
          </Box>
        </Fade>
      )}

      {/* Active Session */}
      {isSessionActive && (
        <Box>
          {/* Progress Panel */}
          <GlassCard sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" sx={{ color: 'white', mb: 2, fontWeight: 600 }}>
              📊 Learning Progress
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Box sx={{ mb: 2 }}>
                  <Typography sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 1 }}>
                    Understanding Level
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={progress.understanding_level} 
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: 'rgba(255, 255, 255, 0.2)',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: '#4CAF50'
                      }
                    }}
                  />
                  <Typography sx={{ color: 'white', mt: 1, fontWeight: 600 }}>
                    {progress.understanding_level}%
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Chip
                    icon={<LightbulbOutlined />}
                    label={`${progress.discoveries_made} Discoveries`}
                    sx={{
                      backgroundColor: 'rgba(255, 193, 7, 0.2)',
                      color: '#FFD54F',
                      border: '1px solid rgba(255, 193, 7, 0.3)',
                      fontWeight: 600
                    }}
                  />
                </Box>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Chip
                    icon={<TrendingUp />}
                    label={`${(progress.engagement_score * 100).toFixed(0)}% Engagement`}
                    sx={{
                      backgroundColor: 'rgba(33, 150, 243, 0.2)',
                      color: '#64B5F6',
                      border: '1px solid rgba(33, 150, 243, 0.3)',
                      fontWeight: 600
                    }}
                  />
                </Box>
              </Grid>
            </Grid>
          </GlassCard>

          {/* Chat Interface */}
          <GlassCard sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ color: 'white', mb: 2, fontWeight: 600 }}>
              💬 Learning Conversation
            </Typography>
            
            {/* Current Question Display */}
            {currentQuestion && (
              <Box sx={{ 
                mb: 3, 
                p: 2, 
                background: 'linear-gradient(135deg, rgba(255, 193, 7, 0.2), rgba(255, 193, 7, 0.1))',
                border: '1px solid rgba(255, 193, 7, 0.3)',
                borderRadius: '12px'
              }}>
                <Typography variant="subtitle2" sx={{ color: '#FFD54F', fontWeight: 600, mb: 1 }}>
                  🎯 Current Focus:
                </Typography>
                <Typography sx={{ color: 'white', fontStyle: 'italic' }}>
                  {currentQuestion}
                </Typography>
              </Box>
            )}
            
            {/* Messages */}
            <Box 
              sx={{ 
                height: '400px', 
                overflowY: 'auto', 
                mb: 3,
                display: 'flex',
                flexDirection: 'column',
                padding: '16px',
                background: 'rgba(0, 0, 0, 0.1)',
                borderRadius: '12px',
                border: '1px solid rgba(255, 255, 255, 0.1)'
              }}
            >
              {messages.map((message, index) => (
                <Fade in={true} key={index}>
                  <ChatBubble isai={message.sender === 'ai'}>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
                      <Avatar
                        sx={{
                          width: 32,
                          height: 32,
                          mr: 2,
                          backgroundColor: message.sender === 'ai' ? '#2196F3' : '#4CAF50'
                        }}
                      >
                        {message.sender === 'ai' ? <Psychology /> : <School />}
                      </Avatar>
                      <Box sx={{ flex: 1 }}>
                        <Typography 
                          sx={{ 
                            color: 'white', 
                            fontWeight: 500,
                            lineHeight: 1.6
                          }}
                        >
                          {message.content}
                        </Typography>
                        {message.discovery_detected && (
                          <Chip
                            icon={<CheckCircle />}
                            label="Discovery Made!"
                            size="small"
                            sx={{
                              mt: 1,
                              backgroundColor: 'rgba(76, 175, 80, 0.3)',
                              color: '#81C784'
                            }}
                          />
                        )}
                      </Box>
                    </Box>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        color: 'rgba(255, 255, 255, 0.6)',
                        display: 'block',
                        textAlign: 'right'
                      }}
                    >
                      {message.timestamp}
                    </Typography>
                  </ChatBubble>
                </Fade>
              ))}
              
              {loading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <CircularProgress size={24} sx={{ color: '#2196F3' }} />
                </Box>
              )}
            </Box>

            {/* Input */}
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                multiline
                maxRows={3}
                placeholder="Share your thoughts, ask questions, or explore ideas..."
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={loading}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    color: 'white',
                    borderRadius: '12px',
                    '& fieldset': {
                      borderColor: 'rgba(255, 255, 255, 0.3)',
                    },
                    '&:hover fieldset': {
                      borderColor: 'rgba(255, 255, 255, 0.4)',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#2196F3',
                    },
                  },
                  '& .MuiOutlinedInput-input::placeholder': {
                    color: 'rgba(255, 255, 255, 0.6)',
                  }
                }}
              />
              <Button
                variant="contained"
                onClick={sendMessage}
                disabled={loading || !currentMessage.trim()}
                sx={{
                  minWidth: '60px',
                  borderRadius: '12px',
                  background: 'linear-gradient(135deg, #2196F3, #1976D2)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #1976D2, #1565C0)',
                  }
                }}
              >
                <SendRounded />
              </Button>
            </Box>

            <Box sx={{ mt: 2, textAlign: 'center' }}>
              {showNextQuestion && (
                <Button
                  variant="contained"
                  onClick={() => {
                    setShowNextQuestion(false);
                    // Continue with the current question set in currentQuestion
                  }}
                  sx={{
                    mr: 2,
                    borderRadius: '12px',
                    background: 'linear-gradient(135deg, #4CAF50, #388E3C)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #388E3C, #2E7D32)',
                    }
                  }}
                >
                  Continue to Next Challenge
                </Button>
              )}
              <Button
                variant="outlined"
                onClick={endSession}
                sx={{
                  color: 'rgba(255, 255, 255, 0.8)',
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                  '&:hover': {
                    borderColor: 'rgba(255, 255, 255, 0.5)',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)'
                  }
                }}
              >
                End Learning Session
              </Button>
            </Box>
          </GlassCard>
        </Box>
      )}
    </Box>
  );
};

export default InteractiveLearning;
