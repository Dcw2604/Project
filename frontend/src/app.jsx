import React, { useState } from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Stack from '@mui/material/Stack';
import Paper from '@mui/material/Paper';
import TextField from '@mui/material/TextField';
import './styles/globals.css';

const App = () => {
  const [currentPage, setCurrentPage] = useState('landing');
  const [user, setUser] = useState(null);

  const handleSignOut = () => {
    setUser(null);
    setCurrentPage('landing');
  };

  const renderCurrentPage = () => {
    if (user?.role === 'student') {
      return <StudentDashboard user={user} setCurrentPage={setCurrentPage} />;
    }
    if (user?.role === 'teacher') {
      return <TeacherDashboard user={user} setCurrentPage={setCurrentPage} />;
    }
    switch (currentPage) {
      case 'landing':
        return <LandingPage setCurrentPage={setCurrentPage} />;
      case 'student-portal':
        return <StudentPortal setCurrentPage={setCurrentPage} setUser={setUser} />;
      case 'student-signup':
        return <StudentSignUp setCurrentPage={setCurrentPage} setUser={setUser} />;
      case 'teacher-portal':
        return <TeacherPortal setCurrentPage={setCurrentPage} setUser={setUser} />;
      case 'teacher-signup':
        return <TeacherSignUp setCurrentPage={setCurrentPage} setUser={setUser} />;
      default:
        return <LandingPage setCurrentPage={setCurrentPage} />;
    }
  };

  return (
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
          {user ? (
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
const StudentPortal = ({ setCurrentPage, setUser }) => {
  const handleLogin = () => {
    setUser({ id: 1, name: 'John Doe', role: 'student', level: 'A2' });
    // Home becomes student dashboard
  };
  return (
    <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 400, width: '100%', textAlign: 'center' }}>
      <Typography variant="h5" fontWeight={700} mb={2}>Student Portal - Sign In</Typography>
      <Stack spacing={2} mb={2}>
        <TextField label="Email" variant="outlined" fullWidth />
        <TextField label="Password" type="password" variant="outlined" fullWidth />
      </Stack>
      <Button variant="contained" color="primary" size="large" onClick={handleLogin} fullWidth>
        Sign In
      </Button>
      <Button color="inherit" sx={{ mt: 1 }} onClick={() => setCurrentPage('student-signup')}>Don't have an account? Sign Up</Button>
      <Button color="inherit" sx={{ mt: 1 }} onClick={() => setCurrentPage('landing')}>Back to Home</Button>
    </Paper>
  );
};

// Student Sign Up
const StudentSignUp = ({ setCurrentPage, setUser }) => {
  const handleSignUp = () => {
    setUser({ id: 1, name: 'John Doe', role: 'student', level: 'A2' });
    setCurrentPage('student-dashboard');
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
const TeacherPortal = ({ setCurrentPage, setUser }) => {
  const handleLogin = () => {
    setUser({ id: 2, name: 'Jane Smith', role: 'teacher', subject: 'Math' });
    // Home becomes teacher dashboard
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
const TeacherSignUp = ({ setCurrentPage, setUser }) => {
  const handleSignUp = () => {
    setUser({ id: 2, name: 'Jane Smith', role: 'teacher', subject: 'Math' });
    setCurrentPage('teacher-dashboard');
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


// Student Dashboard Component
const StudentDashboard = ({ user, setCurrentPage }) => {
  const [subPage, setSubPage] = useState(null);
  if (subPage === 'schedule') return <StudentSchedule onBack={() => setSubPage(null)} />;
  if (subPage === 'chatbot') return <StudentChatbot onBack={() => setSubPage(null)} />;
  if (subPage === 'leveltest') return <StudentLevelTest onBack={() => setSubPage(null)} />;
  if (subPage === 'checklevel') return <StudentCheckLevel onBack={() => setSubPage(null)} />;
  return (
    <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 600, width: '100%', textAlign: 'center' }}>
      <Typography variant="h5" fontWeight={700} mb={2}>Welcome, {user?.name}</Typography>
      <Typography variant="body1" mb={4}>Choose an option:</Typography>
      <Stack spacing={2} mb={2}>
        <Button variant="outlined" color="primary" onClick={() => setSubPage('schedule')}>Schedule Classes</Button>
        <Button variant="outlined" color="primary" onClick={() => setSubPage('chatbot')}>Chatbot Questions</Button>
        <Button variant="outlined" color="primary" onClick={() => setSubPage('leveltest')}>Take Level Test</Button>
        <Button variant="outlined" color="primary" onClick={() => setSubPage('checklevel')}>Check My Level</Button>
      </Stack>
      <Button color="inherit" onClick={() => setCurrentPage('landing')}>Logout</Button>
    </Paper>
  );
};

const StudentSchedule = ({ onBack }) => (
  <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 500, width: '100%', textAlign: 'center' }}>
    <Typography variant="h6" mb={2}>Schedule Classes</Typography>
    <Typography mb={3}>[Class scheduling UI goes here]</Typography>
    <Button variant="outlined" onClick={onBack}>Back to Dashboard</Button>
  </Paper>
);
const StudentChatbot = ({ onBack }) => (
  <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 500, width: '100%', textAlign: 'center' }}>
    <Typography variant="h6" mb={2}>Chatbot Questions</Typography>
    <Typography mb={3}>[Chatbot Q&A UI goes here]</Typography>
    <Button variant="outlined" onClick={onBack}>Back to Dashboard</Button>
  </Paper>
);
const StudentLevelTest = ({ onBack }) => (
  <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 500, width: '100%', textAlign: 'center' }}>
    <Typography variant="h6" mb={2}>Take Level Test</Typography>
    <Typography mb={3}>[Level test UI goes here]</Typography>
    <Button variant="outlined" onClick={onBack}>Back to Dashboard</Button>
  </Paper>
);
const StudentCheckLevel = ({ onBack }) => (
  <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 500, width: '100%', textAlign: 'center' }}>
    <Typography variant="h6" mb={2}>Check My Level</Typography>
    <Typography mb={3}>[Student level info goes here]</Typography>
    <Button variant="outlined" onClick={onBack}>Back to Dashboard</Button>
  </Paper>
);

// Teacher Dashboard Component
const TeacherDashboard = ({ user, setCurrentPage }) => {
  const [subPage, setSubPage] = useState(null);
  if (subPage === 'requests') return <TeacherRequests onBack={() => setSubPage(null)} />;
  if (subPage === 'stats') return <TeacherStats onBack={() => setSubPage(null)} />;
  if (subPage === 'hours') return <TeacherOpenHours onBack={() => setSubPage(null)} />;
  if (subPage === 'documents') return <TeacherDocuments onBack={() => setSubPage(null)} />;
  return (
    <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 600, width: '100%', textAlign: 'center' }}>
      <Typography variant="h5" fontWeight={700} mb={2}>Welcome, {user?.name}</Typography>
      <Typography variant="body1" mb={4}>Choose an option:</Typography>
      <Stack spacing={2} mb={2}>
        <Button variant="outlined" color="success" onClick={() => setSubPage('requests')}>Manage Student Requests</Button>
        <Button variant="outlined" color="success" onClick={() => setSubPage('stats')}>View Student Stats</Button>
        <Button variant="outlined" color="success" onClick={() => setSubPage('hours')}>Set Monthly Open Hours</Button>
        <Button variant="outlined" color="success" onClick={() => setSubPage('documents')}>Add Documents for Chatbot</Button>
      </Stack>
      <Button color="inherit" onClick={() => setCurrentPage('landing')}>Logout</Button>
    </Paper>
  );
};

const TeacherRequests = ({ onBack }) => (
  <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 500, width: '100%', textAlign: 'center' }}>
    <Typography variant="h6" mb={2}>Manage Student Requests</Typography>
    <Typography mb={3}>[Class calendar, accept/deny UI goes here]</Typography>
    <Button variant="outlined" onClick={onBack}>Back to Dashboard</Button>
  </Paper>
);
const TeacherStats = ({ onBack }) => (
  <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 500, width: '100%', textAlign: 'center' }}>
    <Typography variant="h6" mb={2}>View Student Stats</Typography>
    <Typography mb={3}>[Student level/test stats UI goes here]</Typography>
    <Button variant="outlined" onClick={onBack}>Back to Dashboard</Button>
  </Paper>
);
const TeacherOpenHours = ({ onBack }) => (
  <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 500, width: '100%', textAlign: 'center' }}>
    <Typography variant="h6" mb={2}>Set Monthly Open Hours</Typography>
    <Typography mb={3}>[Open hours calendar UI goes here]</Typography>
    <Button variant="outlined" onClick={onBack}>Back to Dashboard</Button>
  </Paper>
);
const TeacherDocuments = ({ onBack }) => (
  <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 500, width: '100%', textAlign: 'center' }}>
    <Typography variant="h6" mb={2}>Add Documents for Chatbot</Typography>
    <Typography mb={3}>[Document upload UI goes here]</Typography>
    <Button variant="outlined" onClick={onBack}>Back to Dashboard</Button>
  </Paper>
);

export default App;
