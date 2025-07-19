import React, { useState } from "react";
import ChatbotQuestions from "./ChatbotQuestions";
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

      {/* Content Area */}
      <ContentBox>
        <TabPanel value={activeTab} index={0}>
          <Box position="absolute" inset={0}>
            <ChatbotQuestions />
          </Box>
        </TabPanel>
        
        <TabPanel value={activeTab} index={1}>
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
        </TabPanel>
      </ContentBox>
    </StyledBox>
  );
};

export default StudentDashboard;
