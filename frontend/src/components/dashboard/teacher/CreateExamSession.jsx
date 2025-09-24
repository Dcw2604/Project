import React, { useState, useEffect } from 'react';
import api from '../../../services/api';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  TextField,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Chip,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  MenuItem,
  IconButton,
  Paper,
  Divider,
  styled,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Checkbox,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  Alert,
  Snackbar,
  CircularProgress,
  Tooltip
} from '@mui/material';
import {
  Add,
  ExpandMore,
  Quiz,
  Timer,
  Topic,
  Settings,
  School,
  CheckCircle,
  Cancel,
  Shuffle,
  Edit,
  Preview,
  Save,
  Search
} from '@mui/icons-material';

// Import API service
// import { examApi } from '../../../services/examApi';

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
  padding: '12px 24px',
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

const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    borderRadius: '12px',
    color: 'white',
    '& fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.3)',
    },
    '&:hover fieldset': {
      borderColor: 'rgba(255, 255, 255, 0.5)',
    },
    '&.Mui-focused fieldset': {
      borderColor: '#10B981',
    },
  },
  '& .MuiInputLabel-root': {
    color: 'rgba(255, 255, 255, 0.8)',
    '&.Mui-focused': {
      color: '#10B981',
    },
  },
}));

const ExamDefineForm = ({ onClose, onSuccess }) => {
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    num_questions: 10,
    time_limit_minutes: 60,
    random_topic_distribution: true,
    is_published: false
  });

  // Data state
  const [topics, setTopics] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [manuallySelectedQuestions, setManuallySelectedQuestions] = useState([]);
  const [topicQuestionCounts, setTopicQuestionCounts] = useState({});

  // UI state
  const [loading, setLoading] = useState(false);
  const [questionsLoading, setQuestionsLoading] = useState(false);
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'success' });
  const [previewMode, setPreviewMode] = useState(false);
  const [questionSearchTerm, setQuestionSearchTerm] = useState('');

  // Load initial data
  useEffect(() => {
    loadTopics();
    loadQuestions();
  }, []);

  const loadTopics = async () => {
    try {
      const response = await api.topics.list();
      setTopics(response.topics || []);
    } catch (error) {
      console.error('Error loading topics:', error);
      showAlert('Error loading topics', 'error');
      // Fallback to mock data for development
      const mockTopics = [
        { id: 1, name: 'Algebra', description: 'Basic algebraic concepts', question_count: 25 },
        { id: 2, name: 'Geometry', description: 'Geometric shapes and calculations', question_count: 30 },
        { id: 3, name: 'Calculus', description: 'Differential and integral calculus', question_count: 20 },
        { id: 4, name: 'Statistics', description: 'Data analysis and probability', question_count: 15 }
      ];
      setTopics(mockTopics);
    }
  };

  const loadQuestions = async () => {
    setQuestionsLoading(true);
    try {
      const response = await api.questions.list();
      setQuestions(response.questions || []);
    } catch (error) {
      console.error('Error loading questions:', error);
      showAlert('Error loading questions', 'error');
      // Fallback to mock data for development
      const mockQuestions = [
        {
          id: 1,
          question_text: 'What is the derivative of x²?',
          topic: 3,
          topic_id: 3,
          topic_name: 'Calculus',
          difficulty_level: 'Medium',
          is_generated: true
        },
        {
          id: 2,
          question_text: 'Solve for x: 2x + 5 = 15',
          topic: 1,
          topic_id: 1,
          topic_name: 'Algebra',
          difficulty_level: 'Easy',
          is_generated: true
        },
        {
          id: 3,
          question_text: 'What is the area of a circle with radius 5?',
          topic: 2,
          topic_id: 2,
          topic_name: 'Geometry',
          difficulty_level: 'Medium',
          is_generated: true
        }
      ];
      setQuestions(mockQuestions);
    } finally {
      setQuestionsLoading(false);
    }
  };

  const showAlert = (message, severity = 'success') => {
    setAlert({ open: true, message, severity });
  };

  const handleFormChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleTopicSelection = (topicId, selected) => {
    if (selected) {
      setSelectedTopics(prev => [...prev, topicId]);
      // Set default question count for new topic
      setTopicQuestionCounts(prev => ({
        ...prev,
        [topicId]: Math.min(5, topics.find(t => t.id === topicId)?.question_count || 5)
      }));
    } else {
      setSelectedTopics(prev => prev.filter(id => id !== topicId));
      setTopicQuestionCounts(prev => {
        const newCounts = { ...prev };
        delete newCounts[topicId];
        return newCounts;
      });
    }
  };

  const handleTopicQuestionCount = (topicId, count) => {
    const maxCount = topics.find(t => t.id === topicId)?.question_count || 0;
    const validCount = Math.max(1, Math.min(count, maxCount));
    setTopicQuestionCounts(prev => ({
      ...prev,
      [topicId]: validCount
    }));
  };

  const handleQuestionSelection = (questionId, selected) => {
    if (selected) {
      setManuallySelectedQuestions(prev => [...prev, questionId]);
    } else {
      setManuallySelectedQuestions(prev => prev.filter(id => id !== questionId));
    }
  };

  const getFilteredQuestions = () => {
    return questions.filter(q =>
      q.question_text.toLowerCase().includes(questionSearchTerm.toLowerCase()) ||
      (q.topic_name && q.topic_name.toLowerCase().includes(questionSearchTerm.toLowerCase()))
    );
  };

  const validateForm = () => {
    if (!formData.title.trim()) {
      showAlert('Please enter a title for the exam', 'error');
      return false;
    }

    if (formData.num_questions < 1 || formData.num_questions > 100) {
      showAlert('Number of questions must be between 1 and 100', 'error');
      return false;
    }

    if (formData.time_limit_minutes < 1 || formData.time_limit_minutes > 300) {
      showAlert('Time limit must be between 1 and 300 minutes', 'error');
      return false;
    }

    if (!formData.random_topic_distribution && selectedTopics.length === 0 && manuallySelectedQuestions.length === 0) {
      showAlert('Please select topics or manually select questions', 'error');
      return false;
    }

    if (!formData.random_topic_distribution && selectedTopics.length > 0) {
      const totalTopicQuestions = Object.values(topicQuestionCounts).reduce((sum, count) => sum + count, 0);
      if (totalTopicQuestions !== formData.num_questions) {
        showAlert(`Total questions from topics (${totalTopicQuestions}) must equal the specified number of questions (${formData.num_questions})`, 'error');
        return false;
      }
    }

    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setLoading(true);
    try {
      const examData = {
        title: formData.title,
        description: formData.description,
        num_questions: formData.num_questions,
        random_topic_distribution: formData.random_topic_distribution,
        is_published: formData.is_published,
        time_limit_seconds: formData.time_limit_minutes * 60,
        topic_ids: selectedTopics,
        selected_question_ids: manuallySelectedQuestions
      };

      console.log('Creating exam session:', examData);
      
      const createdExam = await api.examSessions.create(examData);
      console.log('Exam session created successfully:', createdExam);

      showAlert('Exam session created successfully!', 'success');
      setTimeout(() => {
        onSuccess?.(createdExam);
        onClose?.();
      }, 1500);
    } catch (error) {
      console.error('Error creating exam session:', error);
      showAlert(error.message || 'Error creating exam session', 'error');
    } finally {
      setLoading(false);
    }
  };

  const renderBasicSettings = () => (
    <GlassCard>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Settings /> Basic Settings
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <StyledTextField
              fullWidth
              label="Exam Title"
              value={formData.title}
              onChange={(e) => handleFormChange('title', e.target.value)}
              required
            />
          </Grid>
          <Grid item xs={12}>
            <StyledTextField
              fullWidth
              label="Description"
              value={formData.description}
              onChange={(e) => handleFormChange('description', e.target.value)}
              multiline
              rows={3}
            />
          </Grid>
          <Grid item xs={6}>
            <StyledTextField
              fullWidth
              label="Number of Questions"
              type="number"
              value={formData.num_questions}
              onChange={(e) => handleFormChange('num_questions', parseInt(e.target.value) || 0)}
              inputProps={{ min: 1, max: 100 }}
            />
          </Grid>
          <Grid item xs={6}>
            <StyledTextField
              fullWidth
              label="Time Limit (minutes)"
              type="number"
              value={formData.time_limit_minutes}
              onChange={(e) => handleFormChange('time_limit_minutes', parseInt(e.target.value) || 0)}
              inputProps={{ min: 1, max: 300 }}
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_published}
                  onChange={(e) => handleFormChange('is_published', e.target.checked)}
                  sx={{ '& .MuiSwitch-thumb': { backgroundColor: '#10B981' } }}
                />
              }
              label="Publish immediately"
              sx={{ color: 'white' }}
            />
          </Grid>
        </Grid>
      </CardContent>
    </GlassCard>
  );

  const renderQuestionSelection = () => (
    <GlassCard>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Quiz /> Question Selection
        </Typography>
        
        <FormControl component="fieldset" sx={{ mb: 3 }}>
          <FormLabel component="legend" sx={{ color: 'white', mb: 2 }}>
            Selection Method
          </FormLabel>
          <RadioGroup
            value={formData.random_topic_distribution}
            onChange={(e) => handleFormChange('random_topic_distribution', e.target.value === 'true')}
          >
            <FormControlLabel
              value={true}
              control={<Radio sx={{ color: 'white' }} />}
              label="Random distribution across all topics"
              sx={{ color: 'white' }}
            />
            <FormControlLabel
              value={false}
              control={<Radio sx={{ color: 'white' }} />}
              label="Manual topic/question selection"
              sx={{ color: 'white' }}
            />
          </RadioGroup>
        </FormControl>

        {!formData.random_topic_distribution && (
          <>
            <Accordion sx={{ mb: 2, backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
              <AccordionSummary expandIcon={<ExpandMore sx={{ color: 'white' }} />}>
                <Typography sx={{ color: 'white', display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Topic /> Select Topics ({selectedTopics.length})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  {topics.map((topic) => (
                    <Grid item xs={12} sm={6} key={topic.id}>
                      <Paper sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={selectedTopics.includes(topic.id)}
                              onChange={(e) => handleTopicSelection(topic.id, e.target.checked)}
                              sx={{ color: 'white' }}
                            />
                          }
                          label={
                            <Box>
                              <Typography variant="subtitle2" sx={{ color: 'white' }}>
                                {topic.name}
                              </Typography>
                              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                                {topic.question_count} questions available
                              </Typography>
                            </Box>
                          }
                        />
                        {selectedTopics.includes(topic.id) && (
                          <StyledTextField
                            size="small"
                            label="Questions from this topic"
                            type="number"
                            value={topicQuestionCounts[topic.id] || 0}
                            onChange={(e) => handleTopicQuestionCount(topic.id, parseInt(e.target.value) || 0)}
                            inputProps={{ min: 1, max: topic.question_count }}
                            sx={{ mt: 1, width: '100%' }}
                          />
                        )}
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </AccordionDetails>
            </Accordion>

            <Accordion sx={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
              <AccordionSummary expandIcon={<ExpandMore sx={{ color: 'white' }} />}>
                <Typography sx={{ color: 'white', display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Edit /> Manually Select Questions ({manuallySelectedQuestions.length})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <StyledTextField
                  fullWidth
                  placeholder="Search questions..."
                  value={questionSearchTerm}
                  onChange={(e) => setQuestionSearchTerm(e.target.value)}
                  sx={{ mb: 2 }}
                  InputProps={{
                    startAdornment: <Search sx={{ color: 'white', mr: 1 }} />
                  }}
                />
                
                {questionsLoading ? (
                  <Box display="flex" justifyContent="center" p={2}>
                    <CircularProgress sx={{ color: '#10B981' }} />
                  </Box>
                ) : (
                  <List sx={{ maxHeight: 300, overflow: 'auto' }}>
                    {getFilteredQuestions().map((question) => (
                      <ListItem key={question.id} sx={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', mb: 1, borderRadius: 1 }}>
                        <ListItemIcon>
                          <Checkbox
                            checked={manuallySelectedQuestions.includes(question.id)}
                            onChange={(e) => handleQuestionSelection(question.id, e.target.checked)}
                            sx={{ color: 'white' }}
                          />
                        </ListItemIcon>
                        <ListItemText
                          primary={question.question_text}
                          secondary={
                            <Stack direction="row" spacing={1} sx={{ mt: 0.5 }}>
                              <Chip
                                label={question.topic_name || 'No Topic'}
                                size="small"
                                sx={{ backgroundColor: 'rgba(16, 185, 129, 0.2)', color: 'white' }}
                              />
                              <Chip
                                label={question.difficulty_level || 'N/A'}
                                size="small"
                                sx={{ backgroundColor: 'rgba(255, 255, 255, 0.2)', color: 'white' }}
                              />
                            </Stack>
                          }
                          sx={{ color: 'white' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </AccordionDetails>
            </Accordion>
          </>
        )}
      </CardContent>
    </GlassCard>
  );

  const renderPreview = () => (
    <GlassCard>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Preview /> Exam Preview
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
              Title:
            </Typography>
            <Typography variant="body1" sx={{ color: 'white', mb: 2 }}>
              {formData.title || 'Untitled Exam'}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
              Duration:
            </Typography>
            <Typography variant="body1" sx={{ color: 'white', mb: 2 }}>
              {formData.time_limit_minutes} minutes
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
              Questions:
            </Typography>
            <Typography variant="body1" sx={{ color: 'white', mb: 2 }}>
              {formData.num_questions} questions
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
              Status:
            </Typography>
            <Chip
              label={formData.is_published ? 'Published' : 'Draft'}
              size="small"
              color={formData.is_published ? 'success' : 'default'}
              sx={{ mb: 2 }}
            />
          </Grid>
          {formData.description && (
            <Grid item xs={12}>
              <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                Description:
              </Typography>
              <Typography variant="body2" sx={{ color: 'white' }}>
                {formData.description}
              </Typography>
            </Grid>
          )}
        </Grid>
      </CardContent>
    </GlassCard>
  );

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ color: 'white', mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
        <School /> Create Exam Session
      </Typography>

      {renderBasicSettings()}
      {renderQuestionSelection()}
      {renderPreview()}

      <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
        <ActionButton
          variant="outlined"
          onClick={onClose}
          disabled={loading}
        >
          Cancel
        </ActionButton>
        <ActionButton
          variant="contained"
          onClick={handleSubmit}
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : <Save />}
          sx={{
            background: 'linear-gradient(135deg, #10B981, #059669)',
            '&:hover': {
              background: 'linear-gradient(135deg, #059669, #047857)',
            }
          }}
        >
          {loading ? 'Creating...' : 'Create Exam'}
        </ActionButton>
      </Stack>

      <Snackbar
        open={alert.open}
        autoHideDuration={6000}
        onClose={() => setAlert({ ...alert, open: false })}
      >
        <Alert
          onClose={() => setAlert({ ...alert, open: false })}
          severity={alert.severity}
          sx={{ width: '100%' }}
        >
          {alert.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ExamDefineForm;
