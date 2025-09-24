import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  LinearProgress,
  Chip,
  Stack,
  Container,
  Paper,
  styled,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  TrendingUp,
  EmojiEvents,
  Assessment,
  Timeline,
  School,
  CheckCircle,
  Cancel,
  Timer,
  CalendarToday,
  ExpandMore,
  Psychology
} from '@mui/icons-material';

const StyledContainer = styled(Container)(({ theme }) => ({
  height: 'calc(100vh - 80px)',
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
  marginBottom: '1.5rem',
  color: 'white'
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

const StatCard = styled(GlassCard)(({ theme }) => ({
  height: '160px',
  cursor: 'pointer',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: '0 16px 48px rgba(0, 0, 0, 0.2)',
  }
}));

const CheckLevel = () => {
  const [mathTestResults, setMathTestResults] = useState([]);
  const [overallStats, setOverallStats] = useState({
    totalTests: 0,
    averageScore: 0,
    bestScore: 0,
    timeSpent: 0,
    currentLevel: 'Beginner',
    improvement: 0
  });

  useEffect(() => {
    // Load math test results from localStorage
    const results = JSON.parse(localStorage.getItem('mathTestResults') || '[]');
    setMathTestResults(results);
    
    if (results.length > 0) {
      calculateOverallStats(results);
    }
  }, []);

  const calculateOverallStats = (results) => {
    const totalTests = results.length;
    const totalScore = results.reduce((sum, result) => sum + result.percentage, 0);
    const averageScore = Math.round(totalScore / totalTests);
    const bestScore = Math.max(...results.map(r => r.percentage));
    const totalTime = results.reduce((sum, result) => sum + result.timeUsed, 0);
    
    // Determine current level based on recent performance
    const recentResults = results.slice(-3); // Last 3 tests
    const recentAverage = recentResults.reduce((sum, r) => sum + r.percentage, 0) / recentResults.length;
    
    let currentLevel = 'Beginner';
    if (recentAverage >= 90) {
      currentLevel = 'Advanced';
    } else if (recentAverage >= 70) {
      currentLevel = 'Intermediate';
    } else if (recentAverage >= 50) {
      currentLevel = 'Elementary';
    }
    
    // Calculate improvement (comparing first half vs second half of tests)
    let improvement = 0;
    if (results.length >= 4) {
      const firstHalf = results.slice(0, Math.floor(results.length / 2));
      const secondHalf = results.slice(Math.floor(results.length / 2));
      const firstAvg = firstHalf.reduce((sum, r) => sum + r.percentage, 0) / firstHalf.length;
      const secondAvg = secondHalf.reduce((sum, r) => sum + r.percentage, 0) / secondHalf.length;
      improvement = Math.round(secondAvg - firstAvg);
    }
    
    setOverallStats({
      totalTests,
      averageScore,
      bestScore,
      timeSpent: Math.floor(totalTime / 60), // Convert to minutes
      currentLevel,
      improvement
    });
  };

  const getLevelColor = (level) => {
    switch (level) {
      case 'Advanced': return '#10B981';
      case 'Intermediate': return '#F59E0B';
      case 'Elementary': return '#3B82F6';
      default: return '#EF4444';
    }
  };

  const getAchievements = () => {
    const achievements = [];
    
    if (mathTestResults.length >= 1) {
      achievements.push({ 
        title: 'First Steps', 
        description: 'Completed your first math test', 
        icon: '🎯',
        earned: true 
      });
    }
    
    if (mathTestResults.length >= 5) {
      achievements.push({ 
        title: 'Persistent Learner', 
        description: 'Completed 5 math tests', 
        icon: '📚',
        earned: true 
      });
    }
    
    if (overallStats.bestScore >= 90) {
      achievements.push({ 
        title: 'Math Expert', 
        description: 'Scored 90% or higher', 
        icon: '🏆',
        earned: true 
      });
    }
    
    if (overallStats.improvement > 10) {
      achievements.push({ 
        title: 'Rapid Improvement', 
        description: 'Improved by more than 10%', 
        icon: '📈',
        earned: true 
      });
    }
    
    if (mathTestResults.some(r => r.selectedLevel === 5 && r.percentage >= 70)) {
      achievements.push({ 
        title: 'Advanced Mathematics', 
        description: 'Scored 70%+ on Level 5 test', 
        icon: '🔬',
        earned: true 
      });
    }
    
    // Add some potential achievements
    if (mathTestResults.length < 5) {
      achievements.push({ 
        title: 'Persistent Learner', 
        description: 'Complete 5 math tests', 
        icon: '📚',
        earned: false 
      });
    }
    
    if (overallStats.bestScore < 90) {
      achievements.push({ 
        title: 'Math Expert', 
        description: 'Score 90% or higher', 
        icon: '🏆',
        earned: false 
      });
    }
    
    return achievements;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const achievements = getAchievements();

  if (mathTestResults.length === 0) {
    return (
      <StyledContainer maxWidth="lg">
        <HeaderCard elevation={0}>
          <Typography variant="h3" fontWeight={800} mb={1}>
            Mathematics Progress
          </Typography>
          <Typography variant="h6" sx={{ opacity: 0.9, mb: 3 }}>
            Track your mathematical learning journey
          </Typography>
        </HeaderCard>

        <GlassCard>
          <CardContent sx={{ p: 6, textAlign: 'center' }}>
            <Psychology sx={{ fontSize: '4rem', color: '#3B82F6', mb: 3 }} />
            <Typography variant="h4" fontWeight={700} mb={2}>
              Start Your Math Journey
            </Typography>
            <Typography variant="h6" sx={{ opacity: 0.8, mb: 4 }}>
              Take your first math test to begin tracking your progress and achievements.
            </Typography>
            <Typography variant="body1" sx={{ opacity: 0.7 }}>
              Complete tests to unlock detailed analytics, progress tracking, and achievement badges.
            </Typography>
          </CardContent>
        </GlassCard>
      </StyledContainer>
    );
  }

  return (
    <StyledContainer maxWidth="lg">
      <HeaderCard elevation={0}>
        <Typography variant="h3" fontWeight={800} mb={1}>
          Mathematics Progress Dashboard
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, mb: 3 }}>
          Your mathematical learning journey and achievements
        </Typography>
        <Chip 
          label={`Current Level: ${overallStats.currentLevel}`}
          sx={{ 
            fontSize: '1.1rem',
            fontWeight: 700,
            py: 2,
            px: 3,
            bgcolor: getLevelColor(overallStats.currentLevel),
            color: 'white'
          }}
        />
      </HeaderCard>

      {/* Statistics Overview */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard>
            <CardContent sx={{ p: 3, textAlign: 'center', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <Assessment sx={{ fontSize: '2.5rem', color: '#3B82F6', mb: 1 }} />
              <Typography variant="h4" fontWeight={800}>
                {overallStats.totalTests}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Tests Completed
              </Typography>
            </CardContent>
          </StatCard>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard>
            <CardContent sx={{ p: 3, textAlign: 'center', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <TrendingUp sx={{ fontSize: '2.5rem', color: '#10B981', mb: 1 }} />
              <Typography variant="h4" fontWeight={800}>
                {overallStats.averageScore}%
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Average Score
              </Typography>
            </CardContent>
          </StatCard>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard>
            <CardContent sx={{ p: 3, textAlign: 'center', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <EmojiEvents sx={{ fontSize: '2.5rem', color: '#FFD700', mb: 1 }} />
              <Typography variant="h4" fontWeight={800}>
                {overallStats.bestScore}%
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Best Score
              </Typography>
            </CardContent>
          </StatCard>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard>
            <CardContent sx={{ p: 3, textAlign: 'center', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <Timer sx={{ fontSize: '2.5rem', color: '#F59E0B', mb: 1 }} />
              <Typography variant="h4" fontWeight={800}>
                {overallStats.timeSpent}m
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Time Spent
              </Typography>
            </CardContent>
          </StatCard>
        </Grid>
      </Grid>

      {/* Progress Chart and Achievements */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={8}>
          <GlassCard>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h5" fontWeight={700} mb={3} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Timeline />
                Recent Performance
              </Typography>
              
              {overallStats.improvement !== 0 && (
                <Box mb={3}>
                  <Chip 
                    label={`${overallStats.improvement > 0 ? '+' : ''}${overallStats.improvement}% improvement`}
                    sx={{ 
                      bgcolor: overallStats.improvement > 0 ? '#10B981' : '#EF4444',
                      color: 'white',
                      fontWeight: 600
                    }}
                  />
                </Box>
              )}

              <Stack spacing={2}>
                {mathTestResults.slice(-5).reverse().map((result, index) => (
                  <Box key={index} sx={{ p: 2, borderRadius: 2, bgcolor: 'rgba(255, 255, 255, 0.05)' }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Box>
                        <Typography variant="body1" fontWeight={600}>
                          Level {result.selectedLevel} Test - {result.percentage}%
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.7 }}>
                          {formatDate(result.date)}
                        </Typography>
                      </Box>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Chip 
                          label={result.level}
                          size="small"
                          sx={{ 
                            bgcolor: getLevelColor(result.level),
                            color: 'white'
                          }}
                        />
                        <Typography variant="body2" sx={{ opacity: 0.7 }}>
                          {formatTime(result.timeUsed)}
                        </Typography>
                      </Stack>
                    </Stack>
                    <LinearProgress 
                      variant="determinate" 
                      value={result.percentage} 
                      sx={{
                        mt: 1,
                        height: 6,
                        borderRadius: 3,
                        bgcolor: 'rgba(255, 255, 255, 0.1)',
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 3,
                          bgcolor: getLevelColor(result.level)
                        }
                      }}
                    />
                  </Box>
                ))}
              </Stack>
            </CardContent>
          </GlassCard>
        </Grid>

        <Grid item xs={12} md={4}>
          <GlassCard>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h5" fontWeight={700} mb={3} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <EmojiEvents />
                Achievements
              </Typography>
              
              <Stack spacing={2}>
                {achievements.map((achievement, index) => (
                  <Box 
                    key={index} 
                    sx={{ 
                      p: 2, 
                      borderRadius: 2, 
                      bgcolor: achievement.earned ? 'rgba(16, 185, 129, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                      border: achievement.earned ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(255, 255, 255, 0.1)',
                      opacity: achievement.earned ? 1 : 0.6
                    }}
                  >
                    <Stack direction="row" spacing={2} alignItems="center">
                      <Typography variant="h5">{achievement.icon}</Typography>
                      <Box>
                        <Typography variant="body1" fontWeight={600}>
                          {achievement.title}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.8 }}>
                          {achievement.description}
                        </Typography>
                      </Box>
                      {achievement.earned && (
                        <CheckCircle sx={{ color: '#10B981', ml: 'auto' }} />
                      )}
                    </Stack>
                  </Box>
                ))}
              </Stack>
            </CardContent>
          </GlassCard>
        </Grid>
      </Grid>

      {/* Detailed Test History */}
      <GlassCard>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h5" fontWeight={700} mb={3} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <School />
            Detailed Test History
          </Typography>
          
          <Accordion 
            sx={{ 
              bgcolor: 'rgba(255, 255, 255, 0.05)', 
              color: 'white',
              '&:before': { display: 'none' }
            }}
          >
            <AccordionSummary expandIcon={<ExpandMore sx={{ color: 'white' }} />}>
              <Typography variant="h6" fontWeight={600}>
                All Test Results ({mathTestResults.length} tests)
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <TableContainer sx={{ bgcolor: 'rgba(255, 255, 255, 0.02)', borderRadius: 2 }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Date</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Level</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Score</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Result</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Time</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {mathTestResults.reverse().map((result, index) => (
                      <TableRow key={index}>
                        <TableCell sx={{ color: 'white' }}>
                          {formatDate(result.date)}
                        </TableCell>
                        <TableCell sx={{ color: 'white' }}>
                          Level {result.selectedLevel}
                        </TableCell>
                        <TableCell sx={{ color: 'white' }}>
                          {result.correct}/{result.total} ({result.percentage}%)
                        </TableCell>
                        <TableCell sx={{ color: 'white' }}>
                          <Chip 
                            label={result.level}
                            size="small"
                            sx={{ 
                              bgcolor: getLevelColor(result.level),
                              color: 'white'
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ color: 'white' }}>
                          {formatTime(result.timeUsed)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </AccordionDetails>
          </Accordion>
        </CardContent>
      </GlassCard>
    </StyledContainer>
  );
};

export default CheckLevel;
