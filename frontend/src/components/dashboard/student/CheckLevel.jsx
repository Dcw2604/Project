import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Grid, 
  LinearProgress,
  styled,
  Container,
  Paper,
  Stack,
  Chip,
  Avatar,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Button
} from '@mui/material';
import { 
  TrendingUp, 
  Assessment, 
  EmojiEvents,
  School,
  Timer,
  CheckCircle,
  RadioButtonUnchecked,
  Star,
  Timeline,
  BarChart,
  PieChart,
  Refresh
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
  color: 'white',
  '&:hover': {
    transform: 'translateY(-4px)',
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

const StatsCard = styled(GlassCard)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column'
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

const CheckLevel = () => {
  const [progressData, setProgressData] = useState(null);
  const [achievements, setAchievements] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);

  useEffect(() => {
    // Mock data - replace with actual API calls
    const mockProgressData = {
      currentLevel: 'Intermediate',
      levelColor: '#F59E0B',
      overallProgress: 67,
      totalPoints: 2450,
      pointsToNextLevel: 550,
      nextLevel: 'Advanced',
      subjects: [
        { name: 'Mathematics', progress: 75, level: 'Intermediate', color: '#3B82F6' },
        { name: 'Science', progress: 82, level: 'Intermediate', color: '#10B981' },
        { name: 'English', progress: 58, level: 'Elementary', color: '#F59E0B' },
        { name: 'History', progress: 45, level: 'Beginner', color: '#EF4444' }
      ],
      weeklyStats: {
        studyTime: 12.5,
        testsCompleted: 3,
        averageScore: 78,
        improvement: '+12%'
      }
    };

    const mockAchievements = [
      { id: 1, title: 'First Test Completed', description: 'Completed your first level assessment', icon: '🎯', earned: true, date: '2024-12-15' },
      { id: 2, title: 'Science Explorer', description: 'Scored 80%+ in Science assessment', icon: '🔬', earned: true, date: '2024-12-14' },
      { id: 3, title: 'Study Streak', description: 'Study for 7 consecutive days', icon: '🔥', earned: false, progress: 4 },
      { id: 4, title: 'Math Master', description: 'Complete 10 math exercises', icon: '🧮', earned: false, progress: 6 },
      { id: 5, title: 'Speed Reader', description: 'Complete reading test under 5 minutes', icon: '📚', earned: true, date: '2024-12-13' }
    ];

    const mockActivity = [
      { id: 1, type: 'test', title: 'Mathematics Level Test', score: 85, date: '2 hours ago', icon: <Assessment /> },
      { id: 2, type: 'study', title: 'Science - Photosynthesis', time: '45 min', date: '1 day ago', icon: <School /> },
      { id: 3, type: 'achievement', title: 'Earned "Science Explorer" badge', date: '2 days ago', icon: <EmojiEvents /> },
      { id: 4, type: 'test', title: 'English Comprehension', score: 72, date: '3 days ago', icon: <Assessment /> }
    ];

    setProgressData(mockProgressData);
    setAchievements(mockAchievements);
    setRecentActivity(mockActivity);
  }, []);

  const getLevelColor = (level) => {
    switch (level) {
      case 'Advanced': return '#10B981';
      case 'Intermediate': return '#F59E0B';
      case 'Elementary': return '#3B82F6';
      case 'Beginner': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case 'test': return <Assessment />;
      case 'study': return <School />;
      case 'achievement': return <EmojiEvents />;
      default: return <Timeline />;
    }
  };

  if (!progressData) {
    return (
      <StyledContainer maxWidth="xl">
        <Box display="flex" justifyContent="center" alignItems="center" height="50vh">
          <Typography variant="h6" color="rgba(255, 255, 255, 0.7)">
            Loading progress data...
          </Typography>
        </Box>
      </StyledContainer>
    );
  }

  return (
    <StyledContainer maxWidth="xl">
      <HeaderCard elevation={0}>
        <Typography variant="h3" fontWeight={800} mb={1}>
          Progress Tracking
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, mb: 3 }}>
          Monitor your learning journey and achievements
        </Typography>
        <Stack direction="row" spacing={2} justifyContent="center">
          <ActionButton startIcon={<BarChart />}>
            Detailed Analytics
          </ActionButton>
          <ActionButton startIcon={<Refresh />}>
            Update Progress
          </ActionButton>
        </Stack>
      </HeaderCard>

      {/* Overall Progress Section */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={8}>
          <GlassCard>
            <CardContent sx={{ p: 4 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h5" fontWeight={700} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TrendingUp />
                  Overall Progress
                </Typography>
                <Chip 
                  label={progressData.currentLevel}
                  sx={{ 
                    bgcolor: progressData.levelColor,
                    color: 'white',
                    fontWeight: 600,
                    fontSize: '1rem',
                    px: 2
                  }}
                />
              </Stack>
              
              <Box mb={4}>
                <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body1" fontWeight={600}>
                    Progress to {progressData.nextLevel}
                  </Typography>
                  <Typography variant="body1" fontWeight={600}>
                    {progressData.overallProgress}%
                  </Typography>
                </Stack>
                <LinearProgress 
                  variant="determinate" 
                  value={progressData.overallProgress} 
                  sx={{ 
                    height: 12, 
                    borderRadius: 6,
                    bgcolor: 'rgba(255, 255, 255, 0.2)',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: progressData.levelColor,
                      borderRadius: 6
                    }
                  }} 
                />
                <Typography variant="caption" sx={{ opacity: 0.8, mt: 1, display: 'block' }}>
                  {progressData.pointsToNextLevel} more points needed for {progressData.nextLevel} level
                </Typography>
              </Box>

              <Typography variant="h6" fontWeight={600} mb={2}>Subject Progress</Typography>
              <Grid container spacing={2}>
                {progressData.subjects.map((subject, index) => (
                  <Grid item xs={12} sm={6} key={index}>
                    <Box p={2} sx={{ bgcolor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="body2" fontWeight={600}>
                          {subject.name}
                        </Typography>
                        <Chip 
                          label={subject.level}
                          size="small"
                          sx={{ 
                            bgcolor: subject.color,
                            color: 'white',
                            fontSize: '0.7rem'
                          }}
                        />
                      </Stack>
                      <LinearProgress 
                        variant="determinate" 
                        value={subject.progress} 
                        sx={{ 
                          height: 6, 
                          borderRadius: 3,
                          bgcolor: 'rgba(255, 255, 255, 0.2)',
                          '& .MuiLinearProgress-bar': {
                            bgcolor: subject.color,
                            borderRadius: 3
                          }
                        }} 
                      />
                      <Typography variant="caption" sx={{ opacity: 0.8, mt: 0.5, display: 'block' }}>
                        {subject.progress}% complete
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </GlassCard>
        </Grid>

        <Grid item xs={12} md={4}>
          <Stack spacing={3}>
            {/* Weekly Stats */}
            <StatsCard>
              <CardContent sx={{ p: 3, flex: 1 }}>
                <Typography variant="h6" fontWeight={700} mb={2} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <BarChart />
                  This Week
                </Typography>
                <Stack spacing={2}>
                  <Box>
                    <Stack direction="row" justifyContent="space-between">
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>Study Time</Typography>
                      <Typography variant="body2" fontWeight={600}>{progressData.weeklyStats.studyTime}h</Typography>
                    </Stack>
                  </Box>
                  <Box>
                    <Stack direction="row" justifyContent="space-between">
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>Tests Completed</Typography>
                      <Typography variant="body2" fontWeight={600}>{progressData.weeklyStats.testsCompleted}</Typography>
                    </Stack>
                  </Box>
                  <Box>
                    <Stack direction="row" justifyContent="space-between">
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>Average Score</Typography>
                      <Typography variant="body2" fontWeight={600}>{progressData.weeklyStats.averageScore}%</Typography>
                    </Stack>
                  </Box>
                  <Box>
                    <Stack direction="row" justifyContent="space-between">
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>Improvement</Typography>
                      <Typography variant="body2" fontWeight={600} sx={{ color: '#10B981' }}>
                        {progressData.weeklyStats.improvement}
                      </Typography>
                    </Stack>
                  </Box>
                </Stack>
              </CardContent>
            </StatsCard>

            {/* Total Points */}
            <StatsCard>
              <CardContent sx={{ p: 3, textAlign: 'center' }}>
                <EmojiEvents sx={{ fontSize: '3rem', color: '#FFD700', mb: 1 }} />
                <Typography variant="h4" fontWeight={800} color="#FFD700">
                  {progressData.totalPoints.toLocaleString()}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Total Points Earned
                </Typography>
              </CardContent>
            </StatsCard>
          </Stack>
        </Grid>
      </Grid>

      {/* Achievements and Activity */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <GlassCard>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h5" fontWeight={700} mb={3} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <EmojiEvents />
                Achievements
              </Typography>
              
              <Stack spacing={2}>
                {achievements.map((achievement) => (
                  <Box 
                    key={achievement.id}
                    sx={{ 
                      p: 2, 
                      bgcolor: achievement.earned ? 'rgba(16, 185, 129, 0.1)' : 'rgba(255, 255, 255, 0.05)', 
                      borderRadius: 2,
                      border: `1px solid ${achievement.earned ? 'rgba(16, 185, 129, 0.3)' : 'rgba(255, 255, 255, 0.1)'}`,
                      opacity: achievement.earned ? 1 : 0.7
                    }}
                  >
                    <Stack direction="row" alignItems="center" spacing={2}>
                      <Typography variant="h4">{achievement.icon}</Typography>
                      <Box flex={1}>
                        <Typography variant="body1" fontWeight={600}>
                          {achievement.title}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.8, mb: 1 }}>
                          {achievement.description}
                        </Typography>
                        {achievement.earned ? (
                          <Chip 
                            icon={<CheckCircle />}
                            label={`Earned ${achievement.date}`}
                            size="small"
                            sx={{ bgcolor: '#10B981', color: 'white' }}
                          />
                        ) : (
                          achievement.progress && (
                            <LinearProgress 
                              variant="determinate" 
                              value={(achievement.progress / 10) * 100} 
                              sx={{ 
                                height: 4, 
                                borderRadius: 2,
                                bgcolor: 'rgba(255, 255, 255, 0.2)',
                                '& .MuiLinearProgress-bar': {
                                  bgcolor: '#F59E0B'
                                }
                              }} 
                            />
                          )
                        )}
                      </Box>
                    </Stack>
                  </Box>
                ))}
              </Stack>
            </CardContent>
          </GlassCard>
        </Grid>

        <Grid item xs={12} md={6}>
          <GlassCard>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h5" fontWeight={700} mb={3} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Timeline />
                Recent Activity
              </Typography>
              
              <List sx={{ p: 0 }}>
                {recentActivity.map((activity, index) => (
                  <React.Fragment key={activity.id}>
                    <ListItem sx={{ px: 0, py: 2 }}>
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: 'rgba(255, 255, 255, 0.2)' }}>
                          {activity.icon}
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="body1" fontWeight={600}>
                            {activity.title}
                          </Typography>
                        }
                        secondary={
                          <Stack direction="row" justifyContent="space-between" alignItems="center">
                            <Typography variant="body2" sx={{ opacity: 0.8 }}>
                              {activity.score && `Score: ${activity.score}%`}
                              {activity.time && `Duration: ${activity.time}`}
                            </Typography>
                            <Typography variant="caption" sx={{ opacity: 0.7 }}>
                              {activity.date}
                            </Typography>
                          </Stack>
                        }
                      />
                    </ListItem>
                    {index < recentActivity.length - 1 && (
                      <Divider sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
                    )}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </GlassCard>
        </Grid>
      </Grid>
    </StyledContainer>
  );
};

export default CheckLevel;
