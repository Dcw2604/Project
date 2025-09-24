import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  IconButton,
  Avatar,
  Fab,
  Paper,
  Divider,
  styled,
  Tabs,
  Tab,
  Calendar
} from '@mui/material';
import {
  Schedule,
  Add,
  Event,
  Person,
  AccessTime,
  Subject,
  CheckCircle,
  Cancel,
  Pending,
  Edit,
  Delete,
  Refresh,
  CalendarMonth,
  Today,
  ViewWeek,
  ViewDay,
  FilterList,
  Search
} from '@mui/icons-material';

const GlassCard = styled(Card)(({ theme }) => ({
  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05))',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  borderRadius: '20px',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
  color: 'white',
  marginBottom: '1.5rem'
}));

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: '12px',
  padding: '8px 16px',
  fontWeight: 600,
  textTransform: 'none',
  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1))',
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(255, 255, 255, 0.3)',
  color: 'white',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.2))',
    transform: 'translateY(-2px)',
  }
}));

const TimeSlot = styled(Paper)(({ theme, isBooked, isPast }) => ({
  padding: '12px',
  margin: '4px 0',
  background: isBooked ? 
    'linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1))' :
    isPast ?
    'linear-gradient(135deg, rgba(107, 114, 128, 0.2), rgba(107, 114, 128, 0.1))' :
    'linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05))',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  borderRadius: '12px',
  color: 'white',
  cursor: isBooked || isPast ? 'default' : 'pointer',
  transition: 'all 0.3s ease',
  '&:hover': {
    transform: isBooked || isPast ? 'none' : 'translateY(-2px)',
    boxShadow: isBooked || isPast ? 'none' : '0 8px 25px rgba(0, 0, 0, 0.15)',
  },
  opacity: isPast ? 0.6 : 1
}));

const ManageSchedule = () => {
  const [lessons, setLessons] = useState([
    {
      id: 1,
      student: 'Sarah Johnson',
      subject: 'Mathematics',
      date: '2025-08-01',
      time: '10:00',
      duration: 60,
      status: 'confirmed',
      type: 'regular',
      location: 'Online',
      notes: 'Algebra review session'
    },
    {
      id: 2,
      student: 'Mike Chen',
      subject: 'Physics',
      date: '2025-08-01',
      time: '14:30',
      duration: 90,
      status: 'pending',
      type: 'intensive',
      location: 'Online',
      notes: 'Mechanics and motion'
    },
    {
      id: 3,
      student: 'Emma Davis',
      subject: 'Chemistry',
      date: '2025-08-02',
      time: '15:00',
      duration: 60,
      status: 'confirmed',
      type: 'regular',
      location: 'Online',
      notes: 'Organic chemistry basics'
    },
    {
      id: 4,
      student: 'Alex Rodriguez',
      subject: 'Mathematics',
      date: '2025-08-02',
      time: '11:00',
      duration: 60,
      status: 'cancelled',
      type: 'makeup',
      location: 'Online',
      notes: 'Trigonometry practice'
    },
    {
      id: 5,
      student: 'Lisa Wang',
      subject: 'Physics',
      date: '2025-08-03',
      time: '13:00',
      duration: 90,
      status: 'confirmed',
      type: 'intensive',
      location: 'Online',
      notes: 'Quantum physics introduction'
    }
  ]);

  const [pendingRequests, setPendingRequests] = useState([
    {
      id: 1,
      student: 'John Smith',
      subject: 'Mathematics',
      preferredDate: '2025-08-05',
      preferredTime: '16:00',
      duration: 60,
      type: 'regular',
      message: 'Need help with calculus derivatives',
      requestDate: '2025-07-30'
    },
    {
      id: 2,
      student: 'Maria Garcia',
      subject: 'Chemistry',
      preferredDate: '2025-08-04',
      preferredTime: '10:00',
      duration: 90,
      type: 'intensive',
      message: 'Struggling with chemical reactions',
      requestDate: '2025-07-29'
    }
  ]);

  const [activeTab, setActiveTab] = useState(0);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedLesson, setSelectedLesson] = useState(null);
  const [viewMode, setViewMode] = useState('week'); // 'day', 'week', 'month'

  // Generate time slots for scheduling
  const generateTimeSlots = () => {
    const slots = [];
    for (let hour = 8; hour <= 20; hour++) {
      for (let minute = 0; minute < 60; minute += 30) {
        const time = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
        const isBooked = lessons.some(lesson => 
          lesson.date === selectedDate && lesson.time === time && lesson.status !== 'cancelled'
        );
        const isPast = new Date(`${selectedDate}T${time}`) < new Date();
        
        slots.push({
          time,
          isBooked,
          isPast,
          lesson: isBooked ? lessons.find(l => l.date === selectedDate && l.time === time) : null
        });
      }
    }
    return slots;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed': return '#10B981';
      case 'pending': return '#F59E0B';
      case 'cancelled': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'confirmed': return <CheckCircle />;
      case 'pending': return <Pending />;
      case 'cancelled': return <Cancel />;
      default: return <Event />;
    }
  };

  const handleLessonClick = (lesson) => {
    setSelectedLesson(lesson);
    setDialogOpen(true);
  };

  const handleRequestAction = (requestId, action) => {
    if (action === 'approve') {
      const request = pendingRequests.find(r => r.id === requestId);
      if (request) {
        const newLesson = {
          id: lessons.length + 1,
          student: request.student,
          subject: request.subject,
          date: request.preferredDate,
          time: request.preferredTime,
          duration: request.duration,
          status: 'confirmed',
          type: request.type,
          location: 'Online',
          notes: request.message
        };
        setLessons([...lessons, newLesson]);
        setPendingRequests(pendingRequests.filter(r => r.id !== requestId));
      }
    } else {
      setPendingRequests(pendingRequests.filter(r => r.id !== requestId));
    }
  };

  const renderCalendarView = () => {
    const timeSlots = generateTimeSlots();
    
    return (
      <GlassCard>
        <CardContent sx={{ p: 3 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h6" fontWeight={700}>
              Schedule for {selectedDate}
            </Typography>
            <Stack direction="row" spacing={2}>
              <TextField
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: 'white',
                    '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                    '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                  }
                }}
              />
              <ActionButton startIcon={<Add />}>
                Add Lesson
              </ActionButton>
            </Stack>
          </Stack>

          <Grid container spacing={2}>
            {timeSlots.map((slot, index) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
                <TimeSlot 
                  isBooked={slot.isBooked} 
                  isPast={slot.isPast}
                  onClick={() => slot.lesson && handleLessonClick(slot.lesson)}
                >
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2" fontWeight={600}>
                      {slot.time}
                    </Typography>
                    {slot.isBooked && slot.lesson && (
                      <Chip 
                        label={slot.lesson.status}
                        size="small"
                        sx={{ 
                          bgcolor: getStatusColor(slot.lesson.status),
                          color: 'white'
                        }}
                      />
                    )}
                  </Stack>
                  
                  {slot.isBooked && slot.lesson ? (
                    <Box mt={1}>
                      <Typography variant="body2" fontWeight={600}>
                        {slot.lesson.student}
                      </Typography>
                      <Typography variant="caption" sx={{ opacity: 0.8 }}>
                        {slot.lesson.subject} • {slot.lesson.duration}min
                      </Typography>
                    </Box>
                  ) : slot.isPast ? (
                    <Typography variant="caption" sx={{ opacity: 0.6 }}>
                      Past
                    </Typography>
                  ) : (
                    <Typography variant="caption" sx={{ opacity: 0.8 }}>
                      Available
                    </Typography>
                  )}
                </TimeSlot>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </GlassCard>
    );
  };

  const renderLessonsList = () => (
    <GlassCard>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" fontWeight={700} mb={3}>
          Upcoming Lessons
        </Typography>
        
        <Stack spacing={2}>
          {lessons
            .filter(lesson => new Date(lesson.date) >= new Date())
            .sort((a, b) => new Date(`${a.date}T${a.time}`) - new Date(`${b.date}T${b.time}`))
            .map((lesson) => (
              <Paper 
                key={lesson.id}
                sx={{
                  p: 3,
                  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05))',
                  backdropFilter: 'blur(20px)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '12px',
                  color: 'white',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)',
                  }
                }}
                onClick={() => handleLessonClick(lesson)}
              >
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Stack direction="row" spacing={3} alignItems="center">
                    <Avatar sx={{ bgcolor: getStatusColor(lesson.status) }}>
                      {lesson.student.charAt(0)}
                    </Avatar>
                    <Box>
                      <Typography variant="h6" fontWeight={700}>
                        {lesson.student}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.8 }}>
                        {lesson.subject} • {lesson.duration} minutes
                      </Typography>
                    </Box>
                    <Box textAlign="center">
                      <Typography variant="body2" fontWeight={600}>
                        {lesson.date}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.8 }}>
                        {lesson.time}
                      </Typography>
                    </Box>
                  </Stack>
                  
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Chip 
                      icon={getStatusIcon(lesson.status)}
                      label={lesson.status}
                      sx={{ 
                        bgcolor: getStatusColor(lesson.status),
                        color: 'white',
                        textTransform: 'capitalize'
                      }}
                    />
                    <IconButton sx={{ color: 'white' }}>
                      <Edit />
                    </IconButton>
                  </Stack>
                </Stack>
              </Paper>
            ))}
        </Stack>
      </CardContent>
    </GlassCard>
  );

  const renderPendingRequests = () => (
    <GlassCard>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" fontWeight={700} mb={3}>
          Pending Lesson Requests
        </Typography>
        
        <Stack spacing={2}>
          {pendingRequests.map((request) => (
            <Paper 
              key={request.id}
              sx={{
                p: 3,
                background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05))',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(245, 158, 11, 0.3)',
                borderRadius: '12px',
                color: 'white'
              }}
            >
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Stack spacing={1}>
                  <Typography variant="h6" fontWeight={700}>
                    {request.student}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    {request.subject} • {request.duration} minutes
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Preferred: {request.preferredDate} at {request.preferredTime}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.7 }}>
                    "{request.message}"
                  </Typography>
                </Stack>
                
                <Stack direction="row" spacing={2}>
                  <ActionButton 
                    size="small"
                    sx={{ bgcolor: '#10B981' }}
                    onClick={() => handleRequestAction(request.id, 'approve')}
                  >
                    Approve
                  </ActionButton>
                  <ActionButton 
                    size="small"
                    sx={{ bgcolor: '#EF4444' }}
                    onClick={() => handleRequestAction(request.id, 'decline')}
                  >
                    Decline
                  </ActionButton>
                </Stack>
              </Stack>
            </Paper>
          ))}
        </Stack>
      </CardContent>
    </GlassCard>
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" fontWeight={800} color="white" mb={1}>
            Schedule Management
          </Typography>
          <Typography variant="h6" sx={{ opacity: 0.9, color: 'white' }}>
            Manage lessons and availability
          </Typography>
        </Box>
        <Stack direction="row" spacing={2}>
          <ActionButton startIcon={<Refresh />}>
            Refresh
          </ActionButton>
          <ActionButton startIcon={<Add />}>
            New Lesson
          </ActionButton>
        </Stack>
      </Stack>

      {/* Statistics */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <GlassCard>
            <CardContent sx={{ p: 3, textAlign: 'center' }}>
              <Event sx={{ fontSize: '2.5rem', color: '#3B82F6', mb: 1 }} />
              <Typography variant="h4" fontWeight={800}>
                {lessons.filter(l => l.status === 'confirmed').length}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Confirmed Lessons
              </Typography>
            </CardContent>
          </GlassCard>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <GlassCard>
            <CardContent sx={{ p: 3, textAlign: 'center' }}>
              <Pending sx={{ fontSize: '2.5rem', color: '#F59E0B', mb: 1 }} />
              <Typography variant="h4" fontWeight={800}>
                {pendingRequests.length}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Pending Requests
              </Typography>
            </CardContent>
          </GlassCard>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <GlassCard>
            <CardContent sx={{ p: 3, textAlign: 'center' }}>
              <Today sx={{ fontSize: '2.5rem', color: '#10B981', mb: 1 }} />
              <Typography variant="h4" fontWeight={800}>
                {lessons.filter(l => l.date === new Date().toISOString().split('T')[0]).length}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Today's Lessons
              </Typography>
            </CardContent>
          </GlassCard>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <GlassCard>
            <CardContent sx={{ p: 3, textAlign: 'center' }}>
              <AccessTime sx={{ fontSize: '2.5rem', color: '#8B5CF6', mb: 1 }} />
              <Typography variant="h4" fontWeight={800}>
                {lessons.reduce((total, lesson) => total + lesson.duration, 0) / 60}h
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Total Hours
              </Typography>
            </CardContent>
          </GlassCard>
        </Grid>
      </Grid>

      {/* View Toggle */}
      <Box sx={{ mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={(e, newValue) => setActiveTab(newValue)}
          sx={{
            '& .MuiTab-root': {
              color: 'rgba(255, 255, 255, 0.7)',
              fontWeight: 600,
              textTransform: 'none',
            },
            '& .Mui-selected': { color: 'white !important' },
            '& .MuiTabs-indicator': { backgroundColor: '#10B981', height: 3 },
          }}
        >
          <Tab icon={<CalendarMonth />} label="Calendar View" />
          <Tab icon={<Schedule />} label="Lessons List" />
          <Tab icon={<Pending />} label="Pending Requests" />
        </Tabs>
      </Box>

      {/* Content Based on Active Tab */}
      {activeTab === 0 && renderCalendarView()}
      {activeTab === 1 && renderLessonsList()}
      {activeTab === 2 && renderPendingRequests()}

      {/* Lesson Detail Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={() => setDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05))',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            color: 'white'
          }
        }}
      >
        {selectedLesson && (
          <>
            <DialogTitle>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Avatar sx={{ bgcolor: getStatusColor(selectedLesson.status) }}>
                  {selectedLesson.student.charAt(0)}
                </Avatar>
                <Box>
                  <Typography variant="h6" fontWeight={700}>
                    {selectedLesson.student}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    {selectedLesson.subject}
                  </Typography>
                </Box>
              </Stack>
            </DialogTitle>
            
            <DialogContent>
              <Stack spacing={2}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>Date & Time</Typography>
                  <Typography variant="body1" fontWeight={600}>
                    {selectedLesson.date} at {selectedLesson.time}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>Duration</Typography>
                  <Typography variant="body1" fontWeight={600}>
                    {selectedLesson.duration} minutes
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>Status</Typography>
                  <Chip 
                    label={selectedLesson.status}
                    sx={{ 
                      bgcolor: getStatusColor(selectedLesson.status),
                      color: 'white',
                      textTransform: 'capitalize'
                    }}
                  />
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>Notes</Typography>
                  <Typography variant="body1">{selectedLesson.notes}</Typography>
                </Box>
              </Stack>
            </DialogContent>
            
            <DialogActions sx={{ p: 3 }}>
              <ActionButton onClick={() => setDialogOpen(false)}>Close</ActionButton>
              <ActionButton startIcon={<Edit />}>Edit</ActionButton>
              <ActionButton startIcon={<Cancel />} sx={{ bgcolor: '#EF4444' }}>
                Cancel Lesson
              </ActionButton>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default ManageSchedule;
