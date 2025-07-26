import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Grid, 
  Button, 
  Chip, 
  Avatar,
  styled,
  Container,
  Paper,
  Stack,
  Divider,
  IconButton
} from '@mui/material';
import { 
  Schedule, 
  Person, 
  VideoCall, 
  AccessTime, 
  CalendarToday, 
  Add,
  NotificationsActive,
  Star,
  PlayArrow,
  Pause
} from '@mui/icons-material';

const StyledContainer = styled(Container)(({ theme }) => ({
  height: 'calc(100vh - 80px)', // Account for header height
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
  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05))',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  borderRadius: '20px',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    transform: 'translateY(-8px)',
    boxShadow: '0 16px 48px rgba(0, 0, 0, 0.2)',
    border: '1px solid rgba(255, 255, 255, 0.3)',
  }
}));

const HeaderCard = styled(Paper)(({ theme }) => ({
  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1))',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  borderRadius: '24px',
  padding: '2rem',
  marginBottom: '2rem',
  color: 'white',
  textAlign: 'center'
}));

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: '16px',
  padding: '12px 24px',
  fontWeight: 600,
  textTransform: 'none',
  fontSize: '1rem',
  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1))',
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(255, 255, 255, 0.3)',
  color: 'white',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.2))',
    transform: 'translateY(-2px)',
    boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)',
  }
}));

const StudentClasses = () => {
  const [classes, setClasses] = useState([]);
  const [upcomingClasses, setUpcomingClasses] = useState([]);

  useEffect(() => {
    // Mock data for classes - replace with actual API call
    const mockClasses = [
      {
        id: 1,
        title: 'Advanced Mathematics',
        teacher: 'Dr. Sarah Johnson',
        time: '2:00 PM - 3:30 PM',
        date: 'Today',
        status: 'active',
        rating: 4.8,
        studentsCount: 24,
        subject: 'Mathematics',
        color: '#4F46E5'
      },
      {
        id: 2,
        title: 'English Literature',
        teacher: 'Prof. Michael Brown',
        time: '4:00 PM - 5:30 PM',
        date: 'Tomorrow',
        status: 'scheduled',
        rating: 4.9,
        studentsCount: 18,
        subject: 'English',
        color: '#059669'
      },
      {
        id: 3,
        title: 'Science Lab Session',
        teacher: 'Dr. Emily Chen',
        time: '10:00 AM - 11:30 AM',
        date: 'Wed, Dec 18',
        status: 'scheduled',
        rating: 4.7,
        studentsCount: 15,
        subject: 'Science',
        color: '#DC2626'
      }
    ];

    const mockUpcoming = [
      {
        id: 4,
        title: 'History Discussion',
        teacher: 'Mr. David Wilson',
        time: '11:00 AM',
        date: 'In 2 hours',
        status: 'upcoming'
      },
      {
        id: 5,
        title: 'Art Workshop',
        teacher: 'Ms. Lisa Garcia',
        time: '3:00 PM',
        date: 'Today',
        status: 'upcoming'
      }
    ];

    setClasses(mockClasses);
    setUpcomingClasses(mockUpcoming);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#10B981';
      case 'scheduled': return '#3B82F6';
      case 'upcoming': return '#F59E0B';
      default: return '#6B7280';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'active': return 'Live Now';
      case 'scheduled': return 'Scheduled';
      case 'upcoming': return 'Upcoming';
      default: return 'Unknown';
    }
  };

  return (
    <StyledContainer maxWidth="xl">
      <HeaderCard elevation={0}>
        <Typography variant="h3" fontWeight={800} mb={1}>
          My Classes
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, mb: 3 }}>
          Manage your enrolled courses and upcoming sessions
        </Typography>
        <Stack direction="row" spacing={2} justifyContent="center">
          <ActionButton startIcon={<Add />}>
            Browse Classes
          </ActionButton>
          <ActionButton startIcon={<Schedule />}>
            View Schedule
          </ActionButton>
        </Stack>
      </HeaderCard>

      {/* Upcoming Classes Section */}
      {upcomingClasses.length > 0 && (
        <Box mb={4}>
          <Typography variant="h5" fontWeight={700} color="white" mb={2} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <NotificationsActive sx={{ color: '#F59E0B' }} />
            Happening Soon
          </Typography>
          <Grid container spacing={2}>
            {upcomingClasses.map((classItem) => (
              <Grid item xs={12} md={6} key={classItem.id}>
                <GlassCard>
                  <CardContent sx={{ p: 3 }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
                      <Typography variant="h6" fontWeight={700} color="white">
                        {classItem.title}
                      </Typography>
                      <Chip 
                        label={classItem.date}
                        size="small"
                        sx={{ 
                          bgcolor: 'rgba(245, 158, 11, 0.2)',
                          color: '#FCD34D',
                          fontWeight: 600
                        }}
                      />
                    </Stack>
                    <Stack direction="row" alignItems="center" spacing={2} mb={2}>
                      <Avatar sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)' }}>
                        <Person />
                      </Avatar>
                      <Box>
                        <Typography variant="body2" color="rgba(255, 255, 255, 0.9)">
                          {classItem.teacher}
                        </Typography>
                        <Typography variant="body2" color="rgba(255, 255, 255, 0.7)" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <AccessTime sx={{ fontSize: 16 }} />
                          {classItem.time}
                        </Typography>
                      </Box>
                    </Stack>
                    <ActionButton fullWidth startIcon={<VideoCall />}>
                      Join Class
                    </ActionButton>
                  </CardContent>
                </GlassCard>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      <Divider sx={{ my: 4, bgcolor: 'rgba(255, 255, 255, 0.2)' }} />

      {/* All Classes Section */}
      <Typography variant="h5" fontWeight={700} color="white" mb={3} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <CalendarToday />
        All Classes
      </Typography>
      
      <Grid container spacing={3}>
        {classes.map((classItem) => (
          <Grid item xs={12} md={6} lg={4} key={classItem.id}>
            <GlassCard>
              <CardContent sx={{ p: 3 }}>
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" fontWeight={700} color="white" mb={1}>
                      {classItem.title}
                    </Typography>
                    <Chip 
                      label={classItem.subject}
                      size="small"
                      sx={{ 
                        bgcolor: classItem.color,
                        color: 'white',
                        fontWeight: 600,
                        mb: 1
                      }}
                    />
                  </Box>
                  <Chip 
                    label={getStatusText(classItem.status)}
                    size="small"
                    sx={{ 
                      bgcolor: getStatusColor(classItem.status),
                      color: 'white',
                      fontWeight: 600
                    }}
                  />
                </Stack>

                <Stack direction="row" alignItems="center" spacing={2} mb={2}>
                  <Avatar sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)' }}>
                    <Person />
                  </Avatar>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" color="rgba(255, 255, 255, 0.9)" fontWeight={600}>
                      {classItem.teacher}
                    </Typography>
                    <Stack direction="row" spacing={2} mt={0.5}>
                      <Typography variant="caption" color="rgba(255, 255, 255, 0.7)" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Star sx={{ fontSize: 14, color: '#FCD34D' }} />
                        {classItem.rating}
                      </Typography>
                      <Typography variant="caption" color="rgba(255, 255, 255, 0.7)">
                        {classItem.studentsCount} students
                      </Typography>
                    </Stack>
                  </Box>
                </Stack>

                <Box mb={3}>
                  <Typography variant="body2" color="rgba(255, 255, 255, 0.8)" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <AccessTime sx={{ fontSize: 16 }} />
                    {classItem.time}
                  </Typography>
                  <Typography variant="body2" color="rgba(255, 255, 255, 0.8)" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CalendarToday sx={{ fontSize: 16 }} />
                    {classItem.date}
                  </Typography>
                </Box>

                <Stack direction="row" spacing={1}>
                  {classItem.status === 'active' ? (
                    <ActionButton fullWidth startIcon={<VideoCall />} sx={{ bgcolor: 'rgba(16, 185, 129, 0.2)' }}>
                      Join Live
                    </ActionButton>
                  ) : (
                    <ActionButton fullWidth startIcon={<PlayArrow />}>
                      View Details
                    </ActionButton>
                  )}
                </Stack>
              </CardContent>
            </GlassCard>
          </Grid>
        ))}
      </Grid>

      {classes.length === 0 && (
        <Box textAlign="center" py={8}>
          <Typography variant="h6" color="rgba(255, 255, 255, 0.7)" mb={2}>
            No classes enrolled yet
          </Typography>
          <ActionButton startIcon={<Add />}>
            Browse Available Classes
          </ActionButton>
        </Box>
      )}
    </StyledContainer>
  );
};

export default StudentClasses;
