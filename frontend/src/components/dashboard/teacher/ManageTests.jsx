import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  Stack,
  styled,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Tabs,
  Tab
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Upload,
  FileUpload,
  Description,
  QuestionAnswer
} from '@mui/icons-material';

const StyledCard = styled(Card)(({ theme }) => ({
  background: 'rgba(255, 255, 255, 0.1)',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  borderRadius: '20px',
  color: 'white',
  marginBottom: theme.spacing(3),
}));

const ManageTests = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [documents, setDocuments] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadDialog, setUploadDialog] = useState(false);
  const [questionDialog, setQuestionDialog] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [filterLevel, setFilterLevel] = useState('');
  const [uploadData, setUploadData] = useState({
    title: '',
    file: null
  });
  const [uploadError, setUploadError] = useState('');
  const [questionData, setQuestionData] = useState({
    question_text: '',
    question_type: 'multiple_choice',
    difficulty_level: '3',
    option_a: '',
    option_b: '',
    option_c: '',
    option_d: '',
    correct_answer: '',
    explanation: ''
  });

  const loadDocuments = useCallback(async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch('http://127.0.0.1:8000/api/documents/', {
        headers: {
          'Authorization': `Token ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
      }
    } catch (error) {
      console.error('Error loading documents:', error);
    }
  }, []);

  const loadQuestions = useCallback(async () => {
    try {
      const token = localStorage.getItem('authToken');
      let url = 'http://127.0.0.1:8000/api/questions/';
      if (filterLevel) {
        url += `?difficulty_level=${filterLevel}`;
      }
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Token ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setQuestions(data.questions || []);
      }
    } catch (error) {
      console.error('Error loading questions:', error);
    }
  }, [filterLevel]);

  useEffect(() => {
    loadDocuments();
    loadQuestions();
  }, [loadDocuments, loadQuestions]);

  const validateFile = (file) => {
    const maxSize = 200 * 1024 * 1024; // 200MB in bytes
    
    if (!file) {
      return { valid: false, error: 'Please select a file' };
    }
    
    if (file.size > maxSize) {
      return { 
        valid: false, 
        error: `File size (${(file.size / (1024 * 1024)).toFixed(1)}MB) exceeds the 200MB limit` 
      };
    }
    
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      return { valid: false, error: 'Only PDF files are allowed' };
    }
    
    return { valid: true, error: '' };
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    const validation = validateFile(file);
    
    if (validation.valid) {
      setUploadData({ ...uploadData, file });
      setUploadError('');
    } else {
      setUploadData({ ...uploadData, file: null });
      setUploadError(validation.error);
    }
  };

  const handleOpenUploadDialog = () => {
    setUploadDialog(true);
    setUploadError('');
    setUploadData({ title: '', file: null });
  };

  const handleUploadDocument = async () => {
    if (!uploadData.title || !uploadData.file) {
      alert('Please provide both title and file');
      return;
    }

    // Validate file again before upload
    const validation = validateFile(uploadData.file);
    if (!validation.valid) {
      setUploadError(validation.error);
      return;
    }

    setLoading(true);
    setUploadError('');
    try {
      const token = localStorage.getItem('authToken');
      const formData = new FormData();
      formData.append('title', uploadData.title);
      formData.append('file', uploadData.file);
      formData.append('document_type', 'pdf');

      const response = await fetch('http://127.0.0.1:8000/api/upload_document/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        await response.json(); // Just consume the response
        alert('Document uploaded successfully! Questions will be generated automatically.');
        setUploadDialog(false);
        setUploadData({ title: '', file: null });
        loadDocuments();
        // Reload questions after a delay to allow processing
        setTimeout(() => loadQuestions(), 5000);
      } else {
        const errorData = await response.json();
        alert(`Upload failed: ${errorData.error}`);
      }
    } catch (error) {
      alert(`Upload error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDocument = async (documentId) => {
    if (!window.confirm('Are you sure? This will delete the document and all its questions.')) {
      return;
    }

    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`http://127.0.0.1:8000/api/documents/${documentId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Token ${token}`,
        },
      });

      if (response.ok) {
        loadDocuments();
        loadQuestions();
      } else {
        alert('Failed to delete document');
      }
    } catch (error) {
      alert(`Delete error: ${error.message}`);
    }
  };

  const handleSaveQuestion = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const isEdit = selectedQuestion !== null;
      const url = isEdit 
        ? `http://127.0.0.1:8000/api/questions/${selectedQuestion.id}/`
        : 'http://127.0.0.1:8000/api/questions/create/';
      
      const method = isEdit ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(questionData),
      });

      if (response.ok) {
        setQuestionDialog(false);
        setSelectedQuestion(null);
        setQuestionData({
          question_text: '',
          question_type: 'multiple_choice',
          difficulty_level: '3',
          option_a: '',
          option_b: '',
          option_c: '',
          option_d: '',
          correct_answer: '',
          explanation: ''
        });
        loadQuestions();
      } else {
        const errorData = await response.json();
        alert(`Save failed: ${JSON.stringify(errorData.error)}`);
      }
    } catch (error) {
      alert(`Save error: ${error.message}`);
    }
  };

  const handleDeleteQuestion = async (questionId) => {
    if (!window.confirm('Are you sure you want to delete this question?')) {
      return;
    }

    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`http://127.0.0.1:8000/api/questions/${questionId}/delete/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Token ${token}`,
        },
      });

      if (response.ok) {
        loadQuestions();
      } else {
        alert('Failed to delete question');
      }
    } catch (error) {
      alert(`Delete error: ${error.message}`);
    }
  };

  const openEditQuestion = (question) => {
    setSelectedQuestion(question);
    setQuestionData({
      document: question.document,
      question_text: question.question_text,
      question_type: question.question_type,
      difficulty_level: question.difficulty_level,
      option_a: question.option_a || '',
      option_b: question.option_b || '',
      option_c: question.option_c || '',
      option_d: question.option_d || '',
      correct_answer: question.correct_answer,
      explanation: question.explanation || ''
    });
    setQuestionDialog(true);
  };

  const renderDocumentsTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>
          📚 Document Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<Upload />}
          onClick={handleOpenUploadDialog}
          sx={{
            background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
            borderRadius: '12px',
            textTransform: 'none',
            fontWeight: 600
          }}
        >
          Upload Document
        </Button>
      </Box>

      <Grid container spacing={3}>
        {documents.map((doc) => (
          <Grid item xs={12} md={6} lg={4} key={doc.id}>
            <StyledCard>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Description sx={{ fontSize: 40, color: '#10B981', mb: 2 }} />
                  <Chip 
                    label={doc.processing_status} 
                    size="small"
                    color={doc.processing_status === 'completed' ? 'success' : 
                           doc.processing_status === 'failed' ? 'error' : 'warning'}
                  />
                </Box>
                <Typography variant="h6" fontWeight={600} mb={1}>
                  {doc.title}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8, mb: 2 }}>
                  Type: {doc.document_type.toUpperCase()}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8, mb: 2 }}>
                  Uploaded: {new Date(doc.created_at).toLocaleDateString()}
                </Typography>
                <Button
                  variant="outlined"
                  color="error"
                  size="small"
                  startIcon={<Delete />}
                  onClick={() => handleDeleteDocument(doc.id)}
                  sx={{ mt: 1 }}
                >
                  Delete
                </Button>
              </CardContent>
            </StyledCard>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const renderQuestionsTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>
          🧠 Question Bank Management
        </Typography>
        <Stack direction="row" spacing={2}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel sx={{ color: 'white' }}>Filter Level</InputLabel>
            <Select
              value={filterLevel}
              onChange={(e) => {
                setFilterLevel(e.target.value);
                setTimeout(() => loadQuestions(), 100);
              }}
              sx={{ color: 'white', '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.3)' } }}
            >
              <MenuItem value="">All Levels</MenuItem>
              <MenuItem value="3">Level 3 - Basic</MenuItem>
              <MenuItem value="4">Level 4 - Intermediate</MenuItem>
              <MenuItem value="5">Level 5 - Advanced</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => {
              setSelectedQuestion(null);
              setQuestionDialog(true);
            }}
            sx={{
              background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
              borderRadius: '12px',
              textTransform: 'none',
              fontWeight: 600
            }}
          >
            Add Question
          </Button>
        </Stack>
      </Box>

      <StyledCard>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: 'white', fontWeight: 600 }}>Question</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 600 }}>Level</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 600 }}>Type</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 600 }}>Document</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 600 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {questions.map((question) => (
                  <TableRow key={question.id}>
                    <TableCell sx={{ color: 'white' }}>
                      {question.question_text.substring(0, 100)}...
                    </TableCell>
                    <TableCell sx={{ color: 'white' }}>
                      <Chip 
                        label={`Level ${question.difficulty_level}`}
                        size="small"
                        color={question.difficulty_level === '5' ? 'error' : 
                               question.difficulty_level === '4' ? 'warning' : 'success'}
                      />
                    </TableCell>
                    <TableCell sx={{ color: 'white' }}>
                      {question.question_type.replace('_', ' ')}
                    </TableCell>
                    <TableCell sx={{ color: 'white' }}>
                      {question.document_title}
                    </TableCell>
                    <TableCell>
                      <Stack direction="row" spacing={1}>
                        <IconButton
                          size="small"
                          onClick={() => openEditQuestion(question)}
                          sx={{ color: '#10B981' }}
                        >
                          <Edit />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDeleteQuestion(question.id)}
                          sx={{ color: '#EF4444' }}
                        >
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
      </StyledCard>
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight={800} mb={4} sx={{
        background: 'linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%)',
        backgroundClip: 'text',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        textAlign: 'center'
      }}>
        🎯 Test & Question Management
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'rgba(255,255,255,0.2)', mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={(e, newValue) => setActiveTab(newValue)}
          sx={{
            '& .MuiTab-root': {
              color: 'rgba(255, 255, 255, 0.7)',
              fontWeight: 600,
              '&.Mui-selected': {
                color: '#10B981',
              },
            },
            '& .MuiTabs-indicator': {
              backgroundColor: '#10B981',
            },
          }}
        >
          <Tab icon={<Description />} label="Documents" />
          <Tab icon={<QuestionAnswer />} label="Questions" />
        </Tabs>
      </Box>

      {activeTab === 0 && renderDocumentsTab()}
      {activeTab === 1 && renderQuestionsTab()}

      {/* Upload Document Dialog */}
      <Dialog open={uploadDialog} onClose={() => setUploadDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)', color: 'white' }}>
          📤 Upload New Document
        </DialogTitle>
        <DialogContent sx={{ background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)', color: 'white' }}>
          <TextField
            fullWidth
            label="Document Title"
            value={uploadData.title}
            onChange={(e) => setUploadData({ ...uploadData, title: e.target.value })}
            margin="normal"
            sx={{
              '& .MuiInputLabel-root': { color: 'rgba(255,255,255,0.7)' },
              '& .MuiOutlinedInput-root': { 
                color: 'white',
                '& fieldset': { borderColor: 'rgba(255,255,255,0.3)' }
              }
            }}
          />
          <Button
            variant="outlined"
            component="label"
            fullWidth
            startIcon={<FileUpload />}
            sx={{ mt: 2, mb: 2, color: 'white', borderColor: 'rgba(255,255,255,0.3)' }}
          >
            Choose PDF File
            <input
              type="file"
              accept=".pdf"
              hidden
              onChange={handleFileSelect}
            />
          </Button>
          
          {uploadError && (
            <Alert severity="error" sx={{ mt: 1, mb: 1 }}>
              {uploadError}
            </Alert>
          )}
          
          {uploadData.file && (
            <Box sx={{ mt: 1, mb: 1 }}>
              <Typography variant="body2" sx={{ color: '#10B981' }}>
                ✅ Selected: {uploadData.file.name}
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.875rem' }}>
                Size: {(uploadData.file.size / (1024 * 1024)).toFixed(1)}MB (Max: 200MB)
              </Typography>
            </Box>
          )}
          
          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)', fontSize: '0.75rem', mt: 1 }}>
            📄 Supported format: PDF files up to 200MB
          </Typography>
        </DialogContent>
        <DialogActions sx={{ background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)' }}>
          <Button onClick={() => setUploadDialog(false)} sx={{ color: 'white' }}>
            Cancel
          </Button>
          <Button 
            onClick={handleUploadDocument} 
            variant="contained"
            disabled={loading}
            sx={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}
          >
            {loading ? 'Uploading...' : 'Upload'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Question Dialog */}
      <Dialog open={questionDialog} onClose={() => setQuestionDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)', color: 'white' }}>
          {selectedQuestion ? '✏️ Edit Question' : '➕ Add New Question'}
        </DialogTitle>
        <DialogContent sx={{ background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)', color: 'white' }}>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Question Text"
                multiline
                rows={3}
                value={questionData.question_text}
                onChange={(e) => setQuestionData({ ...questionData, question_text: e.target.value })}
                sx={{
                  '& .MuiInputLabel-root': { color: 'rgba(255,255,255,0.7)' },
                  '& .MuiOutlinedInput-root': { 
                    color: 'white',
                    '& fieldset': { borderColor: 'rgba(255,255,255,0.3)' }
                  }
                }}
              />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel sx={{ color: 'rgba(255,255,255,0.7)' }}>Difficulty Level</InputLabel>
                <Select
                  value={questionData.difficulty_level}
                  onChange={(e) => setQuestionData({ ...questionData, difficulty_level: e.target.value })}
                  sx={{ color: 'white', '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.3)' } }}
                >
                  <MenuItem value="3">Level 3 - Basic</MenuItem>
                  <MenuItem value="4">Level 4 - Intermediate</MenuItem>
                  <MenuItem value="5">Level 5 - Advanced</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel sx={{ color: 'rgba(255,255,255,0.7)' }}>Document</InputLabel>
                <Select
                  value={questionData.document || ''}
                  onChange={(e) => setQuestionData({ ...questionData, document: e.target.value })}
                  sx={{ color: 'white', '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.3)' } }}
                >
                  {documents.map((doc) => (
                    <MenuItem key={doc.id} value={doc.id}>{doc.title}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            {['option_a', 'option_b', 'option_c', 'option_d'].map((option, index) => (
              <Grid item xs={6} key={option}>
                <TextField
                  fullWidth
                  label={`Option ${String.fromCharCode(65 + index)}`}
                  value={questionData[option]}
                  onChange={(e) => setQuestionData({ ...questionData, [option]: e.target.value })}
                  sx={{
                    '& .MuiInputLabel-root': { color: 'rgba(255,255,255,0.7)' },
                    '& .MuiOutlinedInput-root': { 
                      color: 'white',
                      '& fieldset': { borderColor: 'rgba(255,255,255,0.3)' }
                    }
                  }}
                />
              </Grid>
            ))}
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Correct Answer"
                value={questionData.correct_answer}
                onChange={(e) => setQuestionData({ ...questionData, correct_answer: e.target.value })}
                sx={{
                  '& .MuiInputLabel-root': { color: 'rgba(255,255,255,0.7)' },
                  '& .MuiOutlinedInput-root': { 
                    color: 'white',
                    '& fieldset': { borderColor: 'rgba(255,255,255,0.3)' }
                  }
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Explanation"
                multiline
                rows={2}
                value={questionData.explanation}
                onChange={(e) => setQuestionData({ ...questionData, explanation: e.target.value })}
                sx={{
                  '& .MuiInputLabel-root': { color: 'rgba(255,255,255,0.7)' },
                  '& .MuiOutlinedInput-root': { 
                    color: 'white',
                    '& fieldset': { borderColor: 'rgba(255,255,255,0.3)' }
                  }
                }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)' }}>
          <Button onClick={() => setQuestionDialog(false)} sx={{ color: 'white' }}>
            Cancel
          </Button>
          <Button 
            onClick={handleSaveQuestion} 
            variant="contained"
            sx={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}
          >
            {selectedQuestion ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ManageTests;
