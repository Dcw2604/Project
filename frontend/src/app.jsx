import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { styled } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Paper from '@mui/material/Paper';
import TextField from '@mui/material/TextField';
import Alert from '@mui/material/Alert';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import { Chat, Schedule, Assignment, TrendingUp, Psychology } from '@mui/icons-material';
import ChatbotQuestions from './components/dashboard/student/ChatbotQuestions';
import StudentClasses from './components/dashboard/student/StudentClasses';
import NewLevelTest from './components/dashboard/student/NewLevelTest';
import CheckLevel from './components/dashboard/student/CheckLevel';
import InteractiveLearning from './components/dashboard/student/InteractiveLearning';
import TeacherDashboard from './components/dashboard/teacher/TeacherDashboard';
import { useAuth } from './hooks/useAuth';
import './styles/globals.css';

// Create a theme instance
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const App = () => {
  const [currentPage, setCurrentPage] = useState('landing');
  const [activeTab, setActiveTab] = useState(0);
  const { user, isAuthenticated, logout } = useAuth();

  // Force re-render when authentication state changes
  useEffect(() => {
    if (isAuthenticated && user) {
      // User just logged in
    }
  }, [isAuthenticated, user]);

  const handleSignOut = () => {
    logout();
    setCurrentPage('landing');
    setActiveTab(0); // Reset tab when signing out
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const renderDashboardContent = () => {
    switch (activeTab) {
      case 0:
        return <ChatbotQuestions />;
      case 1:
        return <StudentClasses />;
      case 2:
        return <InteractiveLearning />;
      case 3:
        return <NewLevelTest />;
      case 4:
        return <CheckLevel />;
      default:
        return <ChatbotQuestions />;
    }
  };

  const renderCurrentPage = () => {
    // If user is authenticated, show appropriate dashboard
    if (isAuthenticated && user) {
      // Check if user is a teacher
      if (user.role === 'teacher') {
        return <TeacherDashboard />;
      }
      
      // Default to student dashboard with tabs
      return (
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', width: '100%', overflow: 'hidden' }}>
          {renderDashboardContent()}
        </Box>
      );
    }
    
    // If not authenticated, show login/signup pages with centered layout
    const content = (() => {
      switch (currentPage) {
        case 'landing':
          return <LandingPage setCurrentPage={setCurrentPage} />;
        case 'student-portal':
          return <StudentPortal setCurrentPage={setCurrentPage} />;
        case 'student-signup':
          return <StudentSignUp setCurrentPage={setCurrentPage} />;
        case 'teacher-portal':
          return <TeacherPortal setCurrentPage={setCurrentPage} />;
        case 'teacher-signup':
          return <TeacherSignUp setCurrentPage={setCurrentPage} />;
        default:
          return <LandingPage setCurrentPage={setCurrentPage} />;
      }
    })();

    return (
      <Box sx={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center', 
        px: 2,
        width: '100%'
      }}>
        {content}
      </Box>
    );
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          position: 'relative',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
            backdropFilter: 'blur(10px)',
            zIndex: 0
          }
        }}
      >
      <AppBar 
        position="sticky" 
        color="inherit" 
        elevation={0} 
        sx={{ 
          background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1))',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          zIndex: 2
        }}
      >
        <Toolbar>
          <Typography 
            variant="h4" 
            component="div" 
            sx={{ 
              flexGrow: 1, 
              fontWeight: 800, 
              color: '#ffffff', 
              letterSpacing: 1,
              textShadow: '0 2px 10px rgba(0,0,0,0.1)'
            }}
          >
            EduConnect
          </Typography>
          {isAuthenticated ? (
            <>
              {/* Only show navigation tabs for students */}
              {user && user.role === 'student' && (
                <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center', mx: 4 }}>
                  <Tabs 
                    value={activeTab} 
                    onChange={handleTabChange}
                    textColor="inherit"
                    TabIndicatorProps={{
                      style: {
                        backgroundColor: 'rgba(255, 255, 255, 0.8)',
                        height: '3px',
                        borderRadius: '2px'
                      }
                    }}
                    sx={{
                      '& .MuiTab-root': {
                        color: 'rgba(255, 255, 255, 0.7)',
                        fontWeight: 600,
                        fontSize: '0.95rem',
                        textTransform: 'none',
                        minWidth: '120px',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          color: 'rgba(255, 255, 255, 0.9)',
                          transform: 'translateY(-2px)'
                        },
                        '&.Mui-selected': {
                          color: '#ffffff',
                          fontWeight: 700
                        }
                      }
                    }}
                  >
                    <Tab 
                      icon={<Chat sx={{ fontSize: '1.2rem' }} />} 
                      label="AI Chatbot" 
                      iconPosition="start"
                    />
                    <Tab 
                      icon={<Schedule sx={{ fontSize: '1.2rem' }} />} 
                      label="My Classes" 
                      iconPosition="start"
                    />
                    <Tab 
                      icon={<Psychology sx={{ fontSize: '1.2rem' }} />} 
                      label="Interactive Learning" 
                      iconPosition="start"
                    />
                    <Tab 
                      icon={<Assignment sx={{ fontSize: '1.2rem' }} />} 
                      label="Level Test" 
                      iconPosition="start"
                    />
                    <Tab 
                      icon={<TrendingUp sx={{ fontSize: '1.2rem' }} />} 
                      label="Progress" 
                      iconPosition="start"
                    />
                  </Tabs>
                </Box>
              )}
              <Button 
                color="inherit" 
                variant="outlined" 
                sx={{ 
                  fontWeight: 600,
                  color: 'white',
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                  background: 'rgba(255, 255, 255, 0.1)',
                  backdropFilter: 'blur(10px)',
                  borderRadius: '12px',
                  px: 3,
                  '&:hover': {
                    background: 'rgba(255, 255, 255, 0.2)',
                    borderColor: 'rgba(255, 255, 255, 0.4)',
                    transform: 'translateY(-2px)',
                  }
                }} 
                onClick={handleSignOut}
              >
                Sign Out
              </Button>
            </>
          ) : null}
        </Toolbar>
      </AppBar>
      <Box sx={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column',
        width: '100%',
        overflow: 'hidden',
        zIndex: 1 
      }}>
        {renderCurrentPage()}
      </Box>
      {/* Only show footer when not authenticated */}
      {!isAuthenticated && (
        <Box 
          component="footer" 
          sx={{ 
            background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1))',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderLeft: 'none',
            borderRight: 'none',
            borderBottom: 'none',
            py: 2, 
            textAlign: 'center', 
            color: 'rgba(255, 255, 255, 0.9)', 
            fontSize: 14,
            fontWeight: 500,
            zIndex: 2
          }}
        >
          © 2025 EduConnect. All rights reserved.
        </Box>
      )}
    </Box>
    </ThemeProvider>
  );
};

const GlassCard = styled(Paper)(({ theme }) => ({
  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05))',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  borderRadius: '24px',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    transform: 'translateY(-8px)',
    boxShadow: '0 16px 48px rgba(0, 0, 0, 0.2)',
    border: '1px solid rgba(255, 255, 255, 0.3)',
  }
}));

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: '16px',
  padding: '16px 32px',
  fontWeight: 700,
  textTransform: 'none',
  fontSize: '1.1rem',
  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1))',
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(255, 255, 255, 0.3)',
  color: 'white',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.2))',
    transform: 'translateY(-4px)',
    boxShadow: '0 12px 32px rgba(0, 0, 0, 0.15)',
  }
}));

const LandingPage = ({ setCurrentPage }) => (
  <GlassCard elevation={0} sx={{ p: 6, mt: 4, maxWidth: 600, width: '100%', textAlign: 'center', color: 'white' }}>
    <Typography variant="h2" fontWeight={900} mb={2} sx={{ 
      background: 'linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%)',
      backgroundClip: 'text',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      textShadow: '0 4px 20px rgba(255,255,255,0.3)'
    }}>
      Welcome to EduConnect
    </Typography>
    <Typography variant="h6" mb={5} sx={{ opacity: 0.9, lineHeight: 1.6 }}>
      Your intelligent learning companion powered by AI. Join thousands of students on their journey to academic excellence.
    </Typography>
    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3} justifyContent="center">
      <ActionButton 
        size="large" 
        sx={{ minWidth: 200, minHeight: 80, fontSize: '1.2rem' }} 
        onClick={() => setCurrentPage('student-portal')}
      >
        🎓 Student Portal
      </ActionButton>
      <ActionButton 
        size="large" 
        sx={{ minWidth: 200, minHeight: 80, fontSize: '1.2rem' }} 
        onClick={() => setCurrentPage('teacher-portal')}
      >
        👨‍🏫 Teacher Portal
      </ActionButton>
    </Stack>
  </GlassCard>
);


// Student Portal (Sign In)
const StudentPortal = ({ setCurrentPage }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { loginWithCredentials } = useAuth();

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      setError('Please enter both username and password');
      return;
    }

    setIsLoading(true);
    setError('');
    
    console.log('Attempting login...');
    const result = await loginWithCredentials(username, password);
    console.log('Login result:', result);
    
    if (result.success) {
      console.log('Login successful');
      // Force navigation to dashboard after successful login
      setTimeout(() => {
        window.location.reload(); // Force a full page refresh to ensure state is updated
      }, 100);
    } else {
      setError(result.error || 'Login failed');
    }
    
    setIsLoading(false);
  };

  return (
    <GlassCard elevation={0} sx={{ p: 5, mt: 4, maxWidth: 450, width: '100%', color: 'white' }}>
      <Typography variant="h4" fontWeight={800} mb={1} textAlign="center" sx={{
        background: 'linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%)',
        backgroundClip: 'text',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
      }}>
        Student Portal
      </Typography>
      <Typography variant="h6" mb={4} textAlign="center" sx={{ opacity: 0.9 }}>
        Sign in to continue your learning journey
      </Typography>
      
      {error && (
        <Alert 
          severity="error" 
          sx={{ 
            mb: 3,
            bgcolor: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: 'white',
            '& .MuiAlert-icon': { color: '#EF4444' }
          }}
        >
          {error}
        </Alert>
      )}
      
      <Box component="form" onSubmit={handleLogin}>
        <Stack spacing={3} mb={4}>
          <TextField 
            label="Username" 
            variant="outlined" 
            fullWidth 
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isLoading}
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: '12px',
                '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
              },
              '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
              '& .MuiOutlinedInput-input': { color: 'white' }
            }}
          />
          <TextField 
            label="Password" 
            type="password" 
            variant="outlined" 
            fullWidth 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: '12px',
                '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
              },
              '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
              '& .MuiOutlinedInput-input': { color: 'white' }
            }}
          />
        </Stack>
        <ActionButton 
          type="submit"
          size="large" 
          fullWidth
          disabled={isLoading}
          sx={{ mb: 2, py: 2 }}
        >
          {isLoading ? '🔄 Signing In...' : '🚀 Sign In'}
        </ActionButton>
      </Box>
      
      <Stack spacing={1} alignItems="center">
        <Button 
          color="inherit" 
          sx={{ 
            color: 'rgba(255, 255, 255, 0.8)', 
            textTransform: 'none',
            '&:hover': { 
              color: 'white',
              bgcolor: 'rgba(255, 255, 255, 0.1)'
            }
          }} 
          onClick={() => setCurrentPage('student-signup')}
        >
          Don't have an account? Sign Up
        </Button>
        <Button 
          color="inherit" 
          sx={{ 
            color: 'rgba(255, 255, 255, 0.8)', 
            textTransform: 'none',
            '&:hover': { 
              color: 'white',
              bgcolor: 'rgba(255, 255, 255, 0.1)'
            }
          }} 
          onClick={() => setCurrentPage('landing')}
        >
          ← Back to Home
        </Button>
      </Stack>
    </GlassCard>
  );
};

// Student Sign Up
const StudentSignUp = ({ setCurrentPage }) => {
  const handleSignUp = () => {
    // TODO: Implement real signup
    alert('Signup functionality coming soon!');
  };
  return (
    <GlassCard elevation={0} sx={{ p: 5, mt: 4, maxWidth: 450, width: '100%', color: 'white' }}>
      <Typography variant="h4" fontWeight={800} mb={1} textAlign="center" sx={{
        background: 'linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%)',
        backgroundClip: 'text',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
      }}>
        Join EduConnect
      </Typography>
      <Typography variant="h6" mb={4} textAlign="center" sx={{ opacity: 0.9 }}>
        Create your student account
      </Typography>
      
      <Stack spacing={3} mb={4}>
        <Stack direction="row" spacing={2}>
          <TextField 
            label="First Name" 
            variant="outlined" 
            fullWidth
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: '12px',
                '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
              },
              '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
              '& .MuiOutlinedInput-input': { color: 'white' }
            }}
          />
          <TextField 
            label="Last Name" 
            variant="outlined" 
            fullWidth
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: '12px',
                '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
              },
              '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
              '& .MuiOutlinedInput-input': { color: 'white' }
            }}
          />
        </Stack>
        <TextField 
          label="Email" 
          variant="outlined" 
          fullWidth
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              borderRadius: '12px',
              '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
              '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
              '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
            },
            '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
            '& .MuiOutlinedInput-input': { color: 'white' }
          }}
        />
        <TextField 
          label="Password" 
          type="password" 
          variant="outlined" 
          fullWidth
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              borderRadius: '12px',
              '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
              '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
              '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
            },
            '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
            '& .MuiOutlinedInput-input': { color: 'white' }
          }}
        />
        <Stack direction="row" spacing={2}>
          <TextField 
            label="Phone Number" 
            variant="outlined" 
            fullWidth
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: '12px',
                '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
              },
              '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
              '& .MuiOutlinedInput-input': { color: 'white' }
            }}
          />
          <TextField 
            label="Age" 
            variant="outlined" 
            fullWidth
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: '12px',
                '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
              },
              '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
              '& .MuiOutlinedInput-input': { color: 'white' }
            }}
          />
        </Stack>
        <Stack direction="row" spacing={2}>
          <TextField 
            label="Class" 
            variant="outlined" 
            fullWidth
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: '12px',
                '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
              },
              '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
              '& .MuiOutlinedInput-input': { color: 'white' }
            }}
          />
          <TextField 
            label="Subject" 
            variant="outlined" 
            fullWidth
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: '12px',
                '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
              },
              '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
              '& .MuiOutlinedInput-input': { color: 'white' }
            }}
          />
        </Stack>
      </Stack>
      
      <ActionButton 
        size="large" 
        onClick={handleSignUp} 
        fullWidth
        sx={{ mb: 2, py: 2 }}
      >
        ✨ Create Account
      </ActionButton>
      
      <Stack spacing={1} alignItems="center">
        <Button 
          color="inherit" 
          sx={{ 
            color: 'rgba(255, 255, 255, 0.8)', 
            textTransform: 'none',
            '&:hover': { 
              color: 'white',
              bgcolor: 'rgba(255, 255, 255, 0.1)'
            }
          }} 
          onClick={() => setCurrentPage('student-portal')}
        >
          Already have an account? Sign In
        </Button>
      </Stack>
    </GlassCard>
  );
};

// Teacher Portal (Sign In)
const TeacherPortal = ({ setCurrentPage }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { loginWithCredentials } = useAuth();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await loginWithCredentials(email, password);
      if (result.success) {
        // Force a page refresh to ensure teacher dashboard loads properly
        window.location.reload();
      } else {
        setError(result.error || 'Invalid credentials');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <GlassCard elevation={0} sx={{ p: 5, mt: 4, maxWidth: 450, width: '100%', color: 'white' }}>
      <Typography variant="h4" fontWeight={800} mb={1} textAlign="center" sx={{
        background: 'linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%)',
        backgroundClip: 'text',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
      }}>
        Teacher Portal
      </Typography>
      <Typography variant="h6" mb={4} textAlign="center" sx={{ opacity: 0.9 }}>
        Empower your teaching with AI
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3, bgcolor: 'rgba(244, 67, 54, 0.1)', color: 'white' }}>
          {error}
        </Alert>
      )}
      
      <form onSubmit={handleLogin}>
        <Stack spacing={3} mb={4}>
          <TextField 
            label="Email or Username" 
            variant="outlined" 
            fullWidth
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading}
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: '12px',
                '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
              },
              '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
              '& .MuiOutlinedInput-input': { color: 'white' }
            }}
          />
          <TextField 
            label="Password" 
            type="password" 
            variant="outlined" 
            fullWidth
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={loading}
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: '12px',
                '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
              },
              '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
              '& .MuiOutlinedInput-input': { color: 'white' }
            }}
          />
        </Stack>
        
        <ActionButton 
          type="submit"
          size="large" 
          fullWidth
          disabled={loading || !email || !password}
          sx={{ mb: 2, py: 2 }}
        >
          {loading ? '🔄 Signing In...' : '🚀 Sign In'}
        </ActionButton>
      </form>
      
      <Stack spacing={1} alignItems="center">
        <Button 
          color="inherit" 
          sx={{ 
            color: 'rgba(255, 255, 255, 0.8)', 
            textTransform: 'none',
            '&:hover': { 
              color: 'white',
              bgcolor: 'rgba(255, 255, 255, 0.1)'
            }
          }} 
          onClick={() => setCurrentPage('teacher-signup')}
        >
          Don't have an account? Sign Up
        </Button>
        <Button 
          color="inherit" 
          sx={{ 
            color: 'rgba(255, 255, 255, 0.8)', 
            textTransform: 'none',
            '&:hover': { 
              color: 'white',
              bgcolor: 'rgba(255, 255, 255, 0.1)'
            }
          }} 
          onClick={() => setCurrentPage('landing')}
        >
          ← Back to Home
        </Button>
      </Stack>
    </GlassCard>
  );
};

// Teacher Sign Up
const TeacherSignUp = ({ setCurrentPage }) => {
  const handleSignUp = () => {
    alert('Teacher signup functionality coming soon!');
  };
  return (
    <GlassCard elevation={0} sx={{ p: 5, mt: 4, maxWidth: 450, width: '100%', color: 'white' }}>
      <Typography variant="h4" fontWeight={800} mb={1} textAlign="center" sx={{
        background: 'linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%)',
        backgroundClip: 'text',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
      }}>
        Join as Educator
      </Typography>
      <Typography variant="h6" mb={4} textAlign="center" sx={{ opacity: 0.9 }}>
        Create your teacher account
      </Typography>
      
      <Stack spacing={3} mb={4}>
        <Stack direction="row" spacing={2}>
          <TextField 
            label="First Name" 
            variant="outlined" 
            fullWidth
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: '12px',
                '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
              },
              '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
              '& .MuiOutlinedInput-input': { color: 'white' }
            }}
          />
          <TextField 
            label="Last Name" 
            variant="outlined" 
            fullWidth
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: '12px',
                '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
              },
              '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
              '& .MuiOutlinedInput-input': { color: 'white' }
            }}
          />
        </Stack>
        <TextField 
          label="Email" 
          variant="outlined" 
          fullWidth
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              borderRadius: '12px',
              '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
              '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
              '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
            },
            '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
            '& .MuiOutlinedInput-input': { color: 'white' }
          }}
        />
        <TextField 
          label="Password" 
          type="password" 
          variant="outlined" 
          fullWidth
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              borderRadius: '12px',
              '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
              '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
              '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
            },
            '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
            '& .MuiOutlinedInput-input': { color: 'white' }
          }}
        />
        <TextField 
          label="Phone Number" 
          variant="outlined" 
          fullWidth
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              borderRadius: '12px',
              '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
              '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
              '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
            },
            '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
            '& .MuiOutlinedInput-input': { color: 'white' }
          }}
        />
        <TextField 
          label="Teaching Subject" 
          variant="outlined" 
          fullWidth
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              borderRadius: '12px',
              '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
              '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
              '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
            },
            '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
            '& .MuiOutlinedInput-input': { color: 'white' }
          }}
        />
        <TextField 
          label="Short Description for Students" 
          variant="outlined" 
          fullWidth 
          multiline 
          rows={3}
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              borderRadius: '12px',
              '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
              '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
              '&.Mui-focused fieldset': { borderColor: 'rgba(255, 255, 255, 0.7)' }
            },
            '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.8)' },
            '& .MuiOutlinedInput-input': { color: 'white' }
          }}
        />
      </Stack>
      
      <ActionButton 
        size="large" 
        onClick={handleSignUp} 
        fullWidth
        sx={{ mb: 2, py: 2 }}
      >
        ✨ Create Teacher Account
      </ActionButton>
      
      <Stack spacing={1} alignItems="center">
        <Button 
          color="inherit" 
          sx={{ 
            color: 'rgba(255, 255, 255, 0.8)', 
            textTransform: 'none',
            '&:hover': { 
              color: 'white',
              bgcolor: 'rgba(255, 255, 255, 0.1)'
            }
          }} 
          onClick={() => setCurrentPage('teacher-portal')}
        >
          Already have an account? Sign In
        </Button>
      </Stack>
    </GlassCard>
  );
};

export default App;