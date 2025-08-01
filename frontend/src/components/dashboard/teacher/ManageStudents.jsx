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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Avatar,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Badge,
  Tabs,
  Tab,
  styled
} from '@mui/material';
import {
  Person,
  School,
  TrendingUp,
  Assignment,
  CheckCircle,
  Cancel,
  Edit,
  Delete,
  Add,
  FilterList,
  Search,
  ExpandMore,
  Email,
  Phone,
  CalendarToday,
  Star,
  Warning,
  Info
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

const ManageStudents = () => {
  const [students, setStudents] = useState([
    {
      id: 1,
      name: 'Sarah Johnson',
      email: 'sarah.j@email.com',
      age: 16,
      grade: '10th',
      subjects: ['Mathematics', 'Physics'],
      averageScore: 88,
      lessonsCompleted: 24,
      lastActive: '2025-08-01',
      status: 'active',
      performance: 'excellent',
      joinDate: '2025-01-15',
      mathLevel: 'Advanced'
    },
    {
      id: 2,
      name: 'Mike Chen',
      email: 'mike.chen@email.com',
      age: 17,
      grade: '11th',
      subjects: ['Chemistry', 'Biology'],
      averageScore: 92,
      lessonsCompleted: 31,
      lastActive: '2025-07-30',
      status: 'active',
      performance: 'excellent',
      joinDate: '2024-12-10',
      mathLevel: 'Intermediate'
    },
    {
      id: 3,
      name: 'Emma Davis',
      email: 'emma.d@email.com',
      age: 15,
      grade: '9th',
      subjects: ['Mathematics', 'English'],
      averageScore: 76,
      lessonsCompleted: 18,
      lastActive: '2025-07-28',
      status: 'needs attention',
      performance: 'good',
      joinDate: '2025-02-20',
      mathLevel: 'Elementary'
    },
    {
      id: 4,
      name: 'Alex Rodriguez',
      email: 'alex.r@email.com',
      age: 16,
      grade: '10th',
      subjects: ['Physics', 'Mathematics'],
      averageScore: 84,
      lessonsCompleted: 22,
      lastActive: '2025-08-01',
      status: 'active',
      performance: 'good',
      joinDate: '2025-01-08',
      mathLevel: 'Intermediate'
    },
    {
      id: 5,
      name: 'Lisa Wang',
      email: 'lisa.w@email.com',
      age: 17,
      grade: '11th',
      subjects: ['Chemistry', 'Mathematics'],
      averageScore: 95,
      lessonsCompleted: 28,
      lastActive: '2025-08-01',
      status: 'active',
      performance: 'excellent',
      joinDate: '2024-11-15',
      mathLevel: 'Advanced'
    }
  ]);

  const [filteredStudents, setFilteredStudents] = useState(students);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    let filtered = students;
    
    if (searchTerm) {
      filtered = filtered.filter(student => 
        student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        student.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        student.subjects.some(subject => subject.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }
    
    if (filterStatus !== 'all') {
      filtered = filtered.filter(student => student.status === filterStatus);
    }
    
    setFilteredStudents(filtered);
  }, [searchTerm, filterStatus, students]);

  const getPerformanceColor = (performance) => {
    switch (performance) {
      case 'excellent': return '#10B981';
      case 'good': return '#3B82F6';
      case 'needs improvement': return '#F59E0B';
      default: return '#EF4444';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <CheckCircle sx={{ color: '#10B981' }} />;
      case 'needs attention': return <Warning sx={{ color: '#F59E0B' }} />;
      case 'inactive': return <Cancel sx={{ color: '#EF4444' }} />;
      default: return <Info sx={{ color: '#3B82F6' }} />;
    }
  };

  const handleStudentClick = (student) => {
    setSelectedStudent(student);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedStudent(null);
  };

  const renderStudentCard = (student) => (
    <Grid item xs={12} md={6} lg={4} key={student.id}>
      <GlassCard sx={{ cursor: 'pointer', height: '280px' }} onClick={() => handleStudentClick(student)}>
        <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Stack direction="row" alignItems="center" spacing={2} mb={2}>
            <Avatar sx={{ bgcolor: getPerformanceColor(student.performance), width: 50, height: 50 }}>
              {student.name.charAt(0)}
            </Avatar>
            <Box flex={1}>
              <Typography variant="h6" fontWeight={700}>
                {student.name}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Grade {student.grade} • Age {student.age}
              </Typography>
            </Box>
            {getStatusIcon(student.status)}
          </Stack>

          <Stack spacing={1} mb={2}>
            <Box display="flex" justifyContent="space-between">
              <Typography variant="body2">Average Score</Typography>
              <Typography variant="body2" fontWeight={600}>{student.averageScore}%</Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={student.averageScore} 
              sx={{
                height: 6,
                borderRadius: 3,
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 3,
                  bgcolor: getPerformanceColor(student.performance)
                }
              }}
            />
          </Stack>

          <Stack direction="row" spacing={1} mb={2} flexWrap="wrap">
            {student.subjects.map((subject) => (
              <Chip 
                key={subject}
                label={subject}
                size="small"
                sx={{ 
                  bgcolor: 'rgba(255, 255, 255, 0.2)',
                  color: 'white',
                  fontSize: '0.75rem'
                }}
              />
            ))}
          </Stack>

          <Box mt="auto">
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                {student.lessonsCompleted} lessons
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Math: {student.mathLevel}
              </Typography>
            </Stack>
          </Box>
        </CardContent>
      </GlassCard>
    </Grid>
  );

  const renderStudentTable = () => (
    <GlassCard>
      <CardContent sx={{ p: 0 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ color: 'white', fontWeight: 600, borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>Student</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 600, borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>Grade</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 600, borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>Subjects</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 600, borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>Average</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 600, borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>Lessons</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 600, borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>Status</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 600, borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredStudents.map((student) => (
                <TableRow key={student.id} sx={{ '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)' } }}>
                  <TableCell sx={{ color: 'white', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
                    <Stack direction="row" alignItems="center" spacing={2}>
                      <Avatar sx={{ bgcolor: getPerformanceColor(student.performance) }}>
                        {student.name.charAt(0)}
                      </Avatar>
                      <Box>
                        <Typography variant="body2" fontWeight={600}>{student.name}</Typography>
                        <Typography variant="caption" sx={{ opacity: 0.7 }}>{student.email}</Typography>
                      </Box>
                    </Stack>
                  </TableCell>
                  <TableCell sx={{ color: 'white', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
                    {student.grade}
                  </TableCell>
                  <TableCell sx={{ color: 'white', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
                    <Stack direction="row" spacing={1}>
                      {student.subjects.slice(0, 2).map((subject) => (
                        <Chip 
                          key={subject}
                          label={subject}
                          size="small"
                          sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)', color: 'white' }}
                        />
                      ))}
                    </Stack>
                  </TableCell>
                  <TableCell sx={{ color: 'white', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
                    <Typography variant="body2" fontWeight={600} sx={{ color: getPerformanceColor(student.performance) }}>
                      {student.averageScore}%
                    </Typography>
                  </TableCell>
                  <TableCell sx={{ color: 'white', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
                    {student.lessonsCompleted}
                  </TableCell>
                  <TableCell sx={{ color: 'white', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
                    <Stack direction="row" alignItems="center" spacing={1}>
                      {getStatusIcon(student.status)}
                      <Typography variant="caption" sx={{ textTransform: 'capitalize' }}>
                        {student.status}
                      </Typography>
                    </Stack>
                  </TableCell>
                  <TableCell sx={{ color: 'white', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
                    <Stack direction="row" spacing={1}>
                      <IconButton size="small" sx={{ color: 'white' }} onClick={() => handleStudentClick(student)}>
                        <Edit />
                      </IconButton>
                      <IconButton size="small" sx={{ color: '#EF4444' }}>
                        <Delete />
                      </IconButton>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </GlassCard>
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" fontWeight={800} color="white" mb={1}>
            Manage Students
          </Typography>
          <Typography variant="h6" sx={{ opacity: 0.9, color: 'white' }}>
            Track student progress and performance
          </Typography>
        </Box>
        <ActionButton startIcon={<Add />}>
          Add New Student
        </ActionButton>
      </Stack>

      {/* Search and Filters */}
      <GlassCard>
        <CardContent sx={{ p: 3 }}>
          <Stack direction="row" spacing={2} alignItems="center">
            <TextField
              placeholder="Search students..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              sx={{
                flex: 1,
                '& .MuiOutlinedInput-root': {
                  color: 'white',
                  '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                  '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                  '&.Mui-focused fieldset': { borderColor: '#10B981' },
                },
                '& .MuiInputBase-input::placeholder': { color: 'rgba(255, 255, 255, 0.7)' }
              }}
              InputProps={{
                startAdornment: <Search sx={{ color: 'rgba(255, 255, 255, 0.7)', mr: 1 }} />
              }}
            />
            <TextField
              select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              sx={{
                minWidth: 150,
                '& .MuiOutlinedInput-root': {
                  color: 'white',
                  '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                  '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.5)' },
                  '&.Mui-focused fieldset': { borderColor: '#10B981' },
                },
                '& .MuiSelect-icon': { color: 'white' }
              }}
            >
              <MenuItem value="all">All Status</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="needs attention">Needs Attention</MenuItem>
              <MenuItem value="inactive">Inactive</MenuItem>
            </TextField>
          </Stack>
        </CardContent>
      </GlassCard>

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
          <Tab label="Card View" />
          <Tab label="Table View" />
        </Tabs>
      </Box>

      {/* Students Display */}
      {activeTab === 0 ? (
        <Grid container spacing={3}>
          {filteredStudents.map(renderStudentCard)}
        </Grid>
      ) : (
        renderStudentTable()
      )}

      {/* Student Detail Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={handleCloseDialog}
        maxWidth="md"
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
        {selectedStudent && (
          <>
            <DialogTitle sx={{ pb: 1 }}>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Avatar sx={{ bgcolor: getPerformanceColor(selectedStudent.performance), width: 60, height: 60 }}>
                  {selectedStudent.name.charAt(0)}
                </Avatar>
                <Box>
                  <Typography variant="h5" fontWeight={700}>
                    {selectedStudent.name}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Grade {selectedStudent.grade} • {selectedStudent.email}
                  </Typography>
                </Box>
              </Stack>
            </DialogTitle>
            
            <DialogContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" fontWeight={600} mb={2}>Academic Performance</Typography>
                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="body2" mb={1}>Average Score</Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={selectedStudent.averageScore} 
                        sx={{
                          height: 8,
                          borderRadius: 4,
                          bgcolor: 'rgba(255, 255, 255, 0.1)',
                          '& .MuiLinearProgress-bar': {
                            borderRadius: 4,
                            bgcolor: getPerformanceColor(selectedStudent.performance)
                          }
                        }}
                      />
                      <Typography variant="body2" sx={{ mt: 1, color: getPerformanceColor(selectedStudent.performance) }}>
                        {selectedStudent.averageScore}% - {selectedStudent.performance}
                      </Typography>
                    </Box>
                    
                    <Box>
                      <Typography variant="body2" mb={1}>Math Level</Typography>
                      <Chip 
                        label={selectedStudent.mathLevel}
                        sx={{ 
                          bgcolor: selectedStudent.mathLevel === 'Advanced' ? '#10B981' :
                                  selectedStudent.mathLevel === 'Intermediate' ? '#3B82F6' : '#F59E0B',
                          color: 'white'
                        }}
                      />
                    </Box>
                  </Stack>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" fontWeight={600} mb={2}>Details</Typography>
                  <Stack spacing={2}>
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body2">Lessons Completed</Typography>
                      <Typography variant="body2" fontWeight={600}>{selectedStudent.lessonsCompleted}</Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body2">Join Date</Typography>
                      <Typography variant="body2" fontWeight={600}>{selectedStudent.joinDate}</Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body2">Last Active</Typography>
                      <Typography variant="body2" fontWeight={600}>{selectedStudent.lastActive}</Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" mb={1}>Subjects</Typography>
                      <Stack direction="row" spacing={1}>
                        {selectedStudent.subjects.map((subject) => (
                          <Chip 
                            key={subject}
                            label={subject}
                            size="small"
                            sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)', color: 'white' }}
                          />
                        ))}
                      </Stack>
                    </Box>
                  </Stack>
                </Grid>
              </Grid>
            </DialogContent>
            
            <DialogActions sx={{ p: 3 }}>
              <ActionButton onClick={handleCloseDialog}>Close</ActionButton>
              <ActionButton startIcon={<Email />}>Send Message</ActionButton>
              <ActionButton startIcon={<CalendarToday />}>Schedule Lesson</ActionButton>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default ManageStudents;
