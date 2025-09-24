import React, { useState } from "react";
import ChatbotQuestions from "./ChatbotQuestions";
<<<<<<< HEAD
import { Box, Tabs, Tab, Paper, Container, styled } from '@mui/material';
import { Chat, Schedule, Assignment, Timeline } from '@mui/icons-material';

// Custom styled components
const StyledBox = styled(Box)(({ theme }) => ({
  minHeight: '100vh',
  backgroundColor: theme.palette.grey[50]
}));

const ContentBox = styled(Box)({
  height: 'calc(100vh - 48px)',
  position: 'relative',
  overflow: 'hidden'
=======
import StudentClasses from "./StudentClasses";
import InteractiveExam from "./InteractiveExam";
import CheckLevel from "./CheckLevel";
import InteractiveLearning from "./InteractiveLearning";
import { Box, Tabs, Tab, Paper, Container, styled } from '@mui/material';
import { Chat, Schedule, Assignment, Timeline, TrendingUp, Psychology } from '@mui/icons-material';

// Custom styled components with modern glassmorphism design
const StyledBox = styled(Box)(({ theme }) => ({
  minHeight: '100vh',
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
}));

const StyledTabs = styled(Tabs)(({ theme }) => ({
  '& .MuiTabs-flexContainer': {
    gap: '8px',
    padding: '16px 0'
  },
  '& .MuiTab-root': {
    minHeight: '64px',
    borderRadius: '16px',
    margin: '0 4px',
    color: 'rgba(255, 255, 255, 0.7)',
    fontWeight: 600,
    fontSize: '0.95rem',
    textTransform: 'none',
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    '&:hover': {
      background: 'rgba(255, 255, 255, 0.2)',
      color: 'rgba(255, 255, 255, 0.9)',
      transform: 'translateY(-2px)',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
    },
    '&.Mui-selected': {
      background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.1))',
      color: '#ffffff',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
      transform: 'translateY(-2px)'
    }
  },
  '& .MuiTabs-indicator': {
    display: 'none'
  }
}));

const TabContainer = styled(Paper)(({ theme }) => ({
  background: 'rgba(255, 255, 255, 0.05)',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '0',
  boxShadow: 'none',
  position: 'relative',
  zIndex: 1
}));

const ContentBox = styled(Box)({
  height: 'calc(100vh - 120px)',
  position: 'relative',
  overflow: 'hidden',
  zIndex: 1
>>>>>>> daniel
});

const TabPanel = ({ children, value, index }) => (
  <div role="tabpanel" hidden={value !== index} style={{ height: '100%' }}>
    {value === index && children}
  </div>
);

const StudentDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);  // Default to chat tab

  const handleChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <StyledBox>
      {/* Navigation Tabs */}
<<<<<<< HEAD
      <Paper elevation={0} sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Container>
          <Tabs 
            value={activeTab} 
            onChange={handleChange}
            aria-label="Dashboard Navigation"
            textColor="primary"
            indicatorColor="primary"
          >
            <Tab icon={<Chat />} label="AI Chatbot" />
            <Tab icon={<Schedule />} label="Class Scheduling" />
            <Tab icon={<Assignment />} label="Level Test" />
            <Tab icon={<Timeline />} label="Progress" />
          </Tabs>
        </Container>
      </Paper>
=======
      <TabContainer elevation={0}>
        <Container>
          <StyledTabs 
            value={activeTab} 
            onChange={handleChange}
            aria-label="Dashboard Navigation"
            variant="fullWidth"
          >
            <Tab 
              icon={<Chat sx={{ fontSize: '1.5rem' }} />} 
              label="AI Chatbot" 
              iconPosition="top"
            />
            <Tab 
              icon={<Schedule sx={{ fontSize: '1.5rem' }} />} 
              label="My Classes" 
              iconPosition="top"
            />
            <Tab 
              icon={<Psychology sx={{ fontSize: '1.5rem' }} />} 
              label="Interactive Learning" 
              iconPosition="top"
            />
            <Tab 
              icon={<Assignment sx={{ fontSize: '1.5rem' }} />} 
              label="Interactive Exam" 
              iconPosition="top"
            />
            <Tab 
              icon={<TrendingUp sx={{ fontSize: '1.5rem' }} />} 
              label="Progress" 
              iconPosition="top"
            />
          </StyledTabs>
        </Container>
      </TabContainer>
>>>>>>> daniel

      {/* Content Area */}
      <ContentBox>
        <TabPanel value={activeTab} index={0}>
          <Box position="absolute" inset={0}>
            <ChatbotQuestions />
          </Box>
        </TabPanel>
        
        <TabPanel value={activeTab} index={1}>
<<<<<<< HEAD
          <Container sx={{ py: 4 }}>
            <Paper sx={{ p: 3 }}>
              Class Scheduling (Coming Soon)
            </Paper>
          </Container>
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <Container sx={{ py: 4 }}>
            <Paper sx={{ p: 3 }}>
              Level Assessment Test (Coming Soon)
            </Paper>
          </Container>
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <Container sx={{ py: 4 }}>
            <Paper sx={{ p: 3 }}>
              Progress Tracking (Coming Soon)
            </Paper>
          </Container>
=======
          <Box position="absolute" inset={0}>
            <StudentClasses />
          </Box>
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <Box position="absolute" inset={0}>
            <InteractiveLearning />
          </Box>
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <Box position="absolute" inset={0}>
            <InteractiveExam />
          </Box>
        </TabPanel>

        <TabPanel value={activeTab} index={4}>
          <Box position="absolute" inset={0}>
            <CheckLevel />
          </Box>
>>>>>>> daniel
        </TabPanel>
      </ContentBox>
    </StyledBox>
  );
};

export default StudentDashboard;
