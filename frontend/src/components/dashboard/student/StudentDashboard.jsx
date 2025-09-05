import React from "react";
import ChatbotQuestions from "./ChatbotQuestions";
import StudentClasses from "./StudentClasses";
import ChatAlgorithmTest from "./ChatAlgorithmTest";
import CheckLevel from "./CheckLevel";
import { Box, styled } from '@mui/material';

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

const ContentBox = styled(Box)({
  height: 'calc(100vh - 120px)',
  position: 'relative',
  overflow: 'hidden',
  zIndex: 1
});

const TabPanel = ({ children, value, index }) => (
  <div role="tabpanel" hidden={value !== index} style={{ height: '100%' }}>
    {value === index && children}
  </div>
);

const StudentDashboard = ({ activeTab = 0 }) => {
  return (
    <StyledBox>
      {/* Content Area */}
      <ContentBox>
        <TabPanel value={activeTab} index={0}>
          <Box position="absolute" inset={0}>
            <ChatbotQuestions />
          </Box>
        </TabPanel>
        
        <TabPanel value={activeTab} index={1}>
          <Box position="absolute" inset={0}>
            <StudentClasses />
          </Box>
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <Box position="absolute" inset={0}>
            <ChatAlgorithmTest />
          </Box>
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <Box position="absolute" inset={0}>
            <CheckLevel />
          </Box>
        </TabPanel>
      </ContentBox>
    </StyledBox>
  );
};

export default StudentDashboard;
