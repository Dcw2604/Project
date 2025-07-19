import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Stack from '@mui/material/Stack';
import Paper from '@mui/material/Paper';
import TextField from '@mui/material/TextField';
import Alert from '@mui/material/Alert';
import StudentDashboard from './components/dashboard/student/StudentDashboard';
import { useAuth } from './hooks/useAuth';
import './styles/globals.css';

// Simple TeacherDashboard placeholder
const TeacherDashboard = ({ user, setCurrentPage }) => (
  <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 600, width: '100%', textAlign: 'center' }}>
    <Typography variant="h5" fontWeight={700} mb={2}>Welcome, {user?.name}</Typography>
    <Typography variant="body1" mb={4}>Teacher Dashboard (Coming Soon)</Typography>
    <Button color="inherit" onClick={() => setCurrentPage('landing')}>Logout</Button>
  </Paper>
);

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
  const [forceRender, setForceRender] = useState(0);
  const { user, isAuthenticated, logout } = useAuth();

  // Force re-render when authentication state changes
  useEffect(() => {
    console.log('Auth state changed:', { isAuthenticated, user, currentPage });
    if (isAuthenticated && user) {
      // User just logged in, force re-render
      setForceRender(prev => prev + 1);
      console.log('User authenticated, forcing render');
    }
  }, [isAuthenticated, user]);

  const handleSignOut = () => {
    logout();
    setCurrentPage('landing');
  };

  const renderCurrentPage = () => {
    // If user is authenticated, always show the dashboard regardless of currentPage
    if (isAuthenticated && user) {
      return <StudentDashboard user={user} setCurrentPage={setCurrentPage} />;
    }
    
    // If not authenticated, show login/signup pages
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
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          background: 'linear-gradient(135deg, #c7d2fe 0%, #e0e7ff 50%, #f3e8ff 100%)',
        }}
      >
      <AppBar position="sticky" color="inherit" elevation={2} sx={{ bgcolor: 'rgba(255,255,255,0.85)', backdropFilter: 'blur(8px)' }}>
        <Toolbar>
          <Typography variant="h4" component="div" sx={{ flexGrow: 1, fontWeight: 800, color: '#4338ca', letterSpacing: 1 }}>
            EduConnect
          </Typography>
          {isAuthenticated ? (
            <Button color="error" variant="outlined" sx={{ fontWeight: 600 }} onClick={handleSignOut}>Sign Out</Button>
          ) : null}
        </Toolbar>
      </AppBar>
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', px: 2 }}>
        {renderCurrentPage()}
      </Box>
      <Box component="footer" sx={{ bgcolor: 'rgba(255,255,255,0.85)', boxShadow: 1, py: 2, textAlign: 'center', color: 'text.secondary', fontSize: 14 }}>
        © 2025 EduConnect. All rights reserved.
      </Box>
    </Box>
    </ThemeProvider>
  );
};

const LandingPage = ({ setCurrentPage }) => (
  <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 500, width: '100%', textAlign: 'center' }}>
    <Typography variant="h4" fontWeight={800} mb={2}>Welcome to EduConnect</Typography>
    <Typography variant="body1" mb={4}>Your one-stop solution for all educational needs.</Typography>
    <Stack direction="row" spacing={4} justifyContent="center">
      <Button variant="contained" color="primary" size="large" sx={{ minWidth: 180, minHeight: 80, fontSize: 22 }} onClick={() => setCurrentPage('student-portal')}>
        Student Portal
      </Button>
      <Button variant="contained" color="success" size="large" sx={{ minWidth: 180, minHeight: 80, fontSize: 22 }} onClick={() => setCurrentPage('teacher-portal')}>
        Teacher Portal
      </Button>
    </Stack>
  </Paper>
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
    <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 400, width: '100%', textAlign: 'center' }}>
      <Typography variant="h5" fontWeight={700} mb={2}>Student Portal - Sign In</Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <Box component="form" onSubmit={handleLogin}>
        <Stack spacing={2} mb={2}>
          <TextField 
            label="Username" 
            variant="outlined" 
            fullWidth 
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isLoading}
          />
          <TextField 
            label="Password" 
            type="password" 
            variant="outlined" 
            fullWidth 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
          />
        </Stack>
        <Button 
          type="submit"
          variant="contained" 
          color="primary" 
          size="large" 
          fullWidth
          disabled={isLoading}
        >
          {isLoading ? 'Signing In...' : 'Sign In'}
        </Button>
      </Box>
      <Button color="inherit" sx={{ mt: 1 }} onClick={() => setCurrentPage('student-signup')}>Don't have an account? Sign Up</Button>
      <Button color="inherit" sx={{ mt: 1 }} onClick={() => setCurrentPage('landing')}>Back to Home</Button>
    </Paper>
  );
};

// Student Sign Up
const StudentSignUp = ({ setCurrentPage }) => {
  const handleSignUp = () => {
    // TODO: Implement real signup
    alert('Signup functionality coming soon!');
  };
  return (
    <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 400, width: '100%', textAlign: 'center' }}>
      <Typography variant="h5" fontWeight={700} mb={2}>Student Portal - Sign Up</Typography>
      <Stack spacing={2} mb={2}>
        <TextField label="First Name" variant="outlined" fullWidth />
        <TextField label="Last Name" variant="outlined" fullWidth />
        <TextField label="Password" type="password" variant="outlined" fullWidth />
        <TextField label="Phone Number" variant="outlined" fullWidth />
        <TextField label="Email" variant="outlined" fullWidth />
        <TextField label="Age" variant="outlined" fullWidth />
        <TextField label="Class" variant="outlined" fullWidth />
        <TextField label="Points" variant="outlined" fullWidth />
        <TextField label="Subject" variant="outlined" fullWidth />
      </Stack>
      <Button variant="contained" color="primary" size="large" onClick={handleSignUp} fullWidth>
        Sign Up
      </Button>
      <Button color="inherit" sx={{ mt: 1 }} onClick={() => setCurrentPage('student-portal')}>Back to Sign In</Button>
    </Paper>
  );
};

// Teacher Portal (Sign In)
const TeacherPortal = ({ setCurrentPage }) => {
  const handleLogin = () => {
    alert('Teacher login functionality coming soon!');
  };
  return (
    <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 400, width: '100%', textAlign: 'center' }}>
      <Typography variant="h5" fontWeight={700} mb={2}>Teacher Portal - Sign In</Typography>
      <Stack spacing={2} mb={2}>
        <TextField label="Email" variant="outlined" fullWidth />
        <TextField label="Password" type="password" variant="outlined" fullWidth />
      </Stack>
      <Button variant="contained" color="success" size="large" onClick={handleLogin} fullWidth>
        Sign In
      </Button>
      <Button color="inherit" sx={{ mt: 1 }} onClick={() => setCurrentPage('teacher-signup')}>Don't have an account? Sign Up</Button>
      <Button color="inherit" sx={{ mt: 1 }} onClick={() => setCurrentPage('landing')}>Back to Home</Button>
    </Paper>
  );
};

// Teacher Sign Up
const TeacherSignUp = ({ setCurrentPage }) => {
  const handleSignUp = () => {
    alert('Teacher signup functionality coming soon!');
  };
  return (
    <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 400, width: '100%', textAlign: 'center' }}>
      <Typography variant="h5" fontWeight={700} mb={2}>Teacher Portal - Sign Up</Typography>
      <Stack spacing={2} mb={2}>
        <TextField label="First Name" variant="outlined" fullWidth />
        <TextField label="Last Name" variant="outlined" fullWidth />
        <TextField label="Email" variant="outlined" fullWidth />
        <TextField label="Password" type="password" variant="outlined" fullWidth />
        <TextField label="Phone Number" variant="outlined" fullWidth />
        <TextField label="Teaching Subject" variant="outlined" fullWidth />
        <TextField label="Short Description for Students" variant="outlined" fullWidth />
      </Stack>
      <Button variant="contained" color="success" size="large" onClick={handleSignUp} fullWidth>
        Sign Up
      </Button>
      <Button color="inherit" sx={{ mt: 1 }} onClick={() => setCurrentPage('teacher-portal')}>Back to Sign In</Button>
    </Paper>
  );
};

export default App;