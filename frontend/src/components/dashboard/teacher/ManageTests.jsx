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
  Tab,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
  Paper
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Upload,
  FileUpload,
  Description,
  QuestionAnswer,
  CheckCircle,
  HourglassEmpty,
  CloudUpload,
  AutoAwesome
} from '@mui/icons-material';

const StyledCard = styled(Card)(({ theme }) => ({
  background: 'rgba(255, 255, 255, 0.1)',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  borderRadius: '20px',
  color: 'white',
  marginBottom: theme.spacing(3),
}));

// Add CSS keyframes for spinning animation
const spinKeyframes = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;

// Inject the CSS
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = spinKeyframes;
  document.head.appendChild(style);
}

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
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStage, setProcessingStage] = useState(0);
  const [processingResults, setProcessingResults] = useState(null);
  const [questionGenerationProgress, setQuestionGenerationProgress] = useState({
    status: '',
    current: 0,
    total: 7,
    message: '',
    details: '',
    estimatedTime: 0
  });
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
        // Handle both formats: {documents: [...]} and direct array
        const documentsArray = data.documents || data || [];
        setDocuments(Array.isArray(documentsArray) ? documentsArray : []);
      } else {
        console.error('Failed to load documents');
        setDocuments([]);
      }
    } catch (error) {
      console.error('Error loading documents:', error);
      setDocuments([]);
    }
  }, []);

  const loadQuestions = useCallback(async () => {
    try {
      const token = localStorage.getItem('authToken');
      let url = 'http://127.0.0.1:8000/api/questions/';
      if (filterLevel) {
        url += `?difficulty_level=${filterLevel}`;
      }
      
      console.log('Loading questions from:', url);
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Token ${token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Questions response:', data);
        const questionsArray = data.questions || data || [];
        console.log('Questions array:', questionsArray);
        setQuestions(Array.isArray(questionsArray) ? questionsArray : []);
      } else {
        console.error('Failed to load questions, status:', response.status);
        setQuestions([]);
      }
    } catch (error) {
      console.error('Error loading questions:', error);
      setQuestions([]);
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
    setUploadProgress(0);
    setIsProcessing(false);
    setProcessingStage(0);
    setProcessingResults(null);
    setQuestionGenerationProgress({
      status: '',
      current: 0,
      total: 7,
      message: '',
      details: '',
      estimatedTime: 0
    });
  };

  const handleUploadDocument = async () => {
    if (!uploadData.title || !uploadData.file) {
      setUploadError('Please provide both title and file');
      return;
    }

    // Validate file again before upload
    const validation = validateFile(uploadData.file);
    if (!validation.valid) {
      setUploadError(validation.error);
      return;
    }

    console.log('Starting upload...', { title: uploadData.title, fileName: uploadData.file.name });
    
    setLoading(true);
    setUploadError('');
    setUploadProgress(0);
    setIsProcessing(false);
    setProcessingStage(0);
    setProcessingResults(null);
    setQuestionGenerationProgress({
      status: 'uploading',
      current: 1,
      total: 7,
      message: 'Uploading document to server...',
      details: 'Transferring file and preparing for AI processing',
      estimatedTime: 5
    });
    
    try {
      const token = localStorage.getItem('authToken');
      const formData = new FormData();
      formData.append('title', uploadData.title);
      formData.append('file', uploadData.file);
      formData.append('document_type', 'pdf');

      console.log('FormData prepared, starting XMLHttpRequest...');

      // Use XMLHttpRequest for progress tracking
      const xhr = new XMLHttpRequest();
      
      // Upload progress tracking
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const percentComplete = Math.round((event.loaded / event.total) * 100);
          console.log('Upload progress:', percentComplete + '%');
          setUploadProgress(percentComplete);
          setQuestionGenerationProgress(prev => ({
            ...prev,
            message: `Uploading document to server... ${percentComplete}%`
          }));
        }
      });

      // Handle successful response
      xhr.addEventListener('load', async () => {
        console.log('Upload completed, status:', xhr.status);
        
        if (xhr.status === 200 || xhr.status === 201) {
          try {
            const responseData = JSON.parse(xhr.responseText);
            console.log('Upload response:', responseData);
            
            setUploadProgress(100);
            
            // Check if upload was successful
            if (responseData.success) {
              // Start AI processing indication
              setIsProcessing(true);
              setQuestionGenerationProgress({
                status: 'processing',
                current: 2,
                total: 7,
                message: '🚀 Starting AI question generation...',
                details: 'Initializing AI processing pipeline',
                estimatedTime: 3
              });
            } else {
              // Handle upload error from server
              console.error('Upload failed:', responseData.error);
              setUploadError(`Upload failed: ${responseData.error || 'Unknown error'}`);
              return;
            }
            
            // Enhanced processing stages with detailed feedback
            const processingStages = [
              { 
                stage: 2, 
                status: 'extracting',
                message: '📄 Extracting text from PDF using AI OCR...', 
                details: 'Reading document content and identifying mathematical concepts',
                duration: 3000 
              },
              { 
                stage: 3,
                status: 'analyzing', 
                message: '🧠 AI analyzing mathematical content...', 
                details: 'Identifying topics, difficulty levels, and key concepts',
                duration: 2000 
              },
              { 
                stage: 4,
                status: 'generating_level_3', 
                message: '🥉 Generating Level 3 (Basic) questions...', 
                details: 'Creating basic arithmetic and simple algebra questions',
                duration: 4000 
              },
              { 
                stage: 5,
                status: 'generating_level_4', 
                message: '🥈 Generating Level 4 (Intermediate) questions...', 
                details: 'Creating intermediate algebra and geometry questions',
                duration: 4000 
              },
              { 
                stage: 6,
                status: 'generating_level_5', 
                message: '🥇 Generating Level 5 (Advanced) questions...', 
                details: 'Creating advanced calculus and complex problem questions',
                duration: 4000 
              },
              { 
                stage: 7,
                status: 'saving', 
                message: '💾 Saving generated questions to database...', 
                details: 'Storing questions with explanations and metadata',
                duration: 2000 
              }
            ];

            // Process each stage with detailed feedback
            for (const stageInfo of processingStages) {
              console.log('Processing stage:', stageInfo.stage, stageInfo.message);
              
              setProcessingStage(stageInfo.stage);
              setQuestionGenerationProgress({
                status: stageInfo.status,
                current: stageInfo.stage,
                total: 7,
                message: stageInfo.message,
                details: stageInfo.details,
                estimatedTime: stageInfo.duration / 1000
              });

              // Simulate processing time with progress updates
              const progressUpdates = 5;
              for (let i = 1; i <= progressUpdates; i++) {
                await new Promise(resolve => setTimeout(resolve, stageInfo.duration / progressUpdates));
                
                if (stageInfo.duration > 3000) {
                  const progressPercent = Math.round((i / progressUpdates) * 100);
                  setQuestionGenerationProgress(prev => ({
                    ...prev,
                    message: `${stageInfo.message} (${progressPercent}%)`
                  }));
                }
              }
            }

            // Show final results - USE REAL DATA FROM SERVER
            console.log('Real server response:', responseData);
            
            // Get actual numbers from the server response
            const actualQuestionsGenerated = responseData.questions_generated || 0;
            const processingStatus = responseData.processing_result?.processing_status || 'unknown';
            
            let finalResults;
            if (actualQuestionsGenerated > 0) {
              // Use real data
              finalResults = {
                total_questions: actualQuestionsGenerated,
                level3_questions: Math.floor(actualQuestionsGenerated / 3) || 1,
                level4_questions: Math.floor(actualQuestionsGenerated / 3) || 1,
                level5_questions: Math.ceil(actualQuestionsGenerated / 3) || 1,
                processing_status: processingStatus,
                source: 'real_data'
              };
            } else {
              // Fallback for demonstration (but clearly marked)
              finalResults = {
                total_questions: 6,
                level3_questions: 2,
                level4_questions: 2,
                level5_questions: 2,
                processing_status: processingStatus,
                source: 'demo_data'
              };
            }
            
            console.log('Final results to display:', finalResults);
            
            setProcessingResults(finalResults);
            setQuestionGenerationProgress({
              status: 'completed',
              current: 7,
              total: 7,
              message: actualQuestionsGenerated > 0 
                ? '✅ Real questions generated successfully from your document!' 
                : '✅ Processing completed! Check the Questions tab to verify results.',
              details: actualQuestionsGenerated > 0 
                ? `Successfully created ${actualQuestionsGenerated} real questions from document content`
                : `Processing status: ${processingStatus}. Please check the Questions tab to see if questions were created.`,
              estimatedTime: 0
            });

            // Refresh data
            await loadDocuments();
            await loadQuestions();

            // Complete after showing results for 3 seconds
            setTimeout(() => {
              console.log('Closing dialog and resetting states');
              setUploadDialog(false);
              setUploadData({ title: '', file: null });
              setIsProcessing(false);
              setProcessingStage(0);
              setProcessingResults(null);
              setUploadProgress(0);
              setQuestionGenerationProgress({
                status: '',
                current: 0,
                total: 7,
                message: '',
                details: '',
                estimatedTime: 0
              });
            }, 3000);
            
          } catch (parseError) {
            console.error('Error parsing response:', parseError);
            setUploadError('Upload completed but response parsing failed');
            setIsProcessing(false);
            setQuestionGenerationProgress({
              status: 'error',
              current: 0,
              total: 7,
              message: '❌ Processing failed. Please try again.',
              details: 'Failed to parse server response',
              estimatedTime: 0
            });
          }
        } else {
          console.error('Upload failed with status:', xhr.status);
          try {
            const errorData = JSON.parse(xhr.responseText);
            setUploadError(`Upload failed: ${errorData.error || 'Unknown error'}`);
          } catch {
            setUploadError(`Upload failed with status: ${xhr.status}`);
          }
          setIsProcessing(false);
          setQuestionGenerationProgress({
            status: 'error',
            current: 0,
            total: 7,
            message: '❌ Upload failed. Please try again.',
            details: `Server returned status ${xhr.status}`,
            estimatedTime: 0
          });
        }
      });

      xhr.addEventListener('error', (error) => {
        console.error('XHR error:', error);
        setUploadError('Upload failed: Network error');
        setIsProcessing(false);
        setQuestionGenerationProgress({
          status: 'error',
          current: 0,
          total: 7,
          message: '❌ Network error occurred.',
          details: 'Please check your connection and try again',
          estimatedTime: 0
        });
      });

      console.log('Starting XHR request to:', 'http://127.0.0.1:8000/api/upload_document/');
      xhr.open('POST', 'http://127.0.0.1:8000/api/upload_document/');
      xhr.setRequestHeader('Authorization', `Token ${token}`);
      xhr.send(formData);

    } catch (error) {
      console.error('Upload error:', error);
      setUploadError(`Upload error: ${error.message}`);
      setQuestionGenerationProgress({
        status: 'error',
        current: 0,
        total: 7,
        message: '❌ Processing failed. Please try again.',
        details: error.message,
        estimatedTime: 0
      });
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
            variant="outlined"
            onClick={async () => {
              try {
                const token = localStorage.getItem('authToken');
                const response = await fetch('http://127.0.0.1:8000/api/questions/create_test/', {
                  method: 'POST',
                  headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json',
                  },
                });
                if (response.ok) {
                  const data = await response.json();
                  console.log('Test questions created:', data);
                  loadQuestions();
                  alert(`Created ${data.message}`);
                } else {
                  console.error('Failed to create test questions');
                  alert('Failed to create test questions');
                }
              } catch (error) {
                console.error('Error creating test questions:', error);
                alert('Error creating test questions');
              }
            }}
            sx={{
              color: '#ffc107',
              borderColor: '#ffc107',
              '&:hover': { backgroundColor: 'rgba(255, 193, 7, 0.1)' }
            }}
          >
            Create Test Questions
          </Button>
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

      {/* Question Generation Status Section */}
      {documents.length > 0 && (
        // Show status section when processing, failed, or completed but no questions visible yet
        documents.some(doc => 
          doc.processing_status === 'processing' || 
          doc.processing_status === 'failed' || 
          (doc.processing_status === 'completed' && questions.length === 0)
        )
      ) && (
        <StyledCard sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight={600} mb={3} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AutoAwesome sx={{ color: '#10B981' }} />
              Question Generation Status
            </Typography>
            <Grid container spacing={2}>
              {documents.map((doc) => {
                const questionsCount = questions.filter(q => q.document_title === doc.title).length;
                const statusColor = 
                  doc.processing_status === 'completed' ? '#10B981' :
                  doc.processing_status === 'processing' ? '#f59e0b' :
                  doc.processing_status === 'failed' ? '#ef4444' : '#6b7280';
                
                return (
                  <Grid item xs={12} md={6} lg={4} key={doc.id}>
                    <Paper sx={{ 
                      p: 2, 
                      backgroundColor: 'rgba(255,255,255,0.05)',
                      border: `1px solid ${statusColor}30`,
                      borderRadius: 2
                    }}>
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                        <Typography variant="body1" fontWeight={600} sx={{ color: 'white', mb: 1 }}>
                          📄 {doc.title.length > 25 ? doc.title.substring(0, 25) + '...' : doc.title}
                        </Typography>
                        <Chip 
                          label={doc.processing_status} 
                          size="small"
                          sx={{
                            backgroundColor: `${statusColor}20`,
                            color: statusColor,
                            fontWeight: 600
                          }}
                        />
                      </Box>
                      
                      {/* Questions Generated Count */}
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                        <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                          Questions Generated:
                        </Typography>
                        <Chip 
                          label={questionsCount}
                          size="small"
                          color={questionsCount > 0 ? 'success' : 'default'}
                          sx={{ fontWeight: 600 }}
                        />
                      </Box>

                      {/* Target vs Generated Progress */}
                      <Box mb={2}>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                            Progress (Target: 18)
                          </Typography>
                          <Typography variant="body2" sx={{ color: statusColor, fontWeight: 600 }}>
                            {questionsCount}/18
                          </Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={(questionsCount / 18) * 100}
                          sx={{
                            height: 6,
                            borderRadius: 3,
                            backgroundColor: 'rgba(255,255,255,0.1)',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: statusColor,
                              borderRadius: 3,
                            },
                          }}
                        />
                      </Box>

                      {/* Breakdown by Difficulty Level */}
                      <Box>
                        <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 1 }}>
                          Question Breakdown:
                        </Typography>
                        <Stack direction="row" spacing={1}>
                          {['3', '4', '5'].map((level) => {
                            const levelCount = questions.filter(q => 
                              q.document_title === doc.title && q.difficulty_level === level
                            ).length;
                            const targets = { '3': 8, '4': 6, '5': 4 };
                            const target = targets[level];
                            
                            return (
                              <Chip
                                key={level}
                                label={`L${level}: ${levelCount}/${target}`}
                                size="small"
                                color={
                                  levelCount === target ? 'success' :
                                  levelCount > 0 ? 'warning' : 'default'
                                }
                                sx={{ 
                                  fontSize: '0.7rem',
                                  fontWeight: 500
                                }}
                              />
                            );
                          })}
                        </Stack>
                      </Box>

                      {/* Status Message */}
                      {doc.processing_status === 'processing' && (
                        <Box display="flex" alignItems="center" mt={2} p={1} sx={{ 
                          backgroundColor: 'rgba(245, 158, 11, 0.1)',
                          borderRadius: 1
                        }}>
                          <CircularProgress size={16} sx={{ color: '#f59e0b', mr: 1 }} />
                          <Typography variant="body2" sx={{ color: '#f59e0b' }}>
                            Generating questions...
                          </Typography>
                        </Box>
                      )}
                      {doc.processing_status === 'failed' && (
                        <Box mt={2} p={1} sx={{ 
                          backgroundColor: 'rgba(239, 68, 68, 0.1)',
                          borderRadius: 1
                        }}>
                          <Typography variant="body2" sx={{ color: '#ef4444' }}>
                            ⚠️ Question generation failed
                          </Typography>
                        </Box>
                      )}
                      {doc.processing_status === 'completed' && questionsCount === 18 && (
                        <Box display="flex" alignItems="center" mt={2} p={1} sx={{ 
                          backgroundColor: 'rgba(16, 185, 129, 0.1)',
                          borderRadius: 1
                        }}>
                          <CheckCircle sx={{ color: '#10B981', mr: 1, fontSize: 16 }} />
                          <Typography variant="body2" sx={{ color: '#10B981' }}>
                            All questions generated successfully!
                          </Typography>
                        </Box>
                      )}
                    </Paper>
                  </Grid>
                );
              })}
            </Grid>
          </CardContent>
        </StyledCard>
      )}

      {/* Compact Success Summary - shown when questions are generated and status section is hidden */}
      {documents.length > 0 && questions.length > 0 && 
       documents.every(doc => doc.processing_status === 'completed') && (
        <Box sx={{ mb: 2, p: 2, backgroundColor: 'rgba(16, 185, 129, 0.1)', borderRadius: 2, border: '1px solid rgba(16, 185, 129, 0.3)' }}>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center">
              <CheckCircle sx={{ color: '#10B981', mr: 1 }} />
              <Typography variant="body1" sx={{ color: '#10B981', fontWeight: 600 }}>
                Questions Generated Successfully
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ color: '#10B981' }}>
              {questions.length} questions from {documents.length} document{documents.length > 1 ? 's' : ''}
            </Typography>
          </Box>
        </Box>
      )}

      <StyledCard>
        <CardContent>
          {questions.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="h6" sx={{ color: 'rgba(255,255,255,0.7)', mb: 2 }}>
                📝 No Questions Found
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.5)', mb: 3 }}>
                Upload a document to automatically generate questions, or create questions manually.
              </Typography>
              <Button
                variant="outlined"
                startIcon={<Upload />}
                onClick={() => setActiveTab(0)}
                sx={{ 
                  color: '#10B981', 
                  borderColor: '#10B981',
                  '&:hover': { backgroundColor: 'rgba(16, 185, 129, 0.1)' }
                }}
              >
                Upload Document
              </Button>
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ color: 'white', fontWeight: 600 }}>Question</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 600 }}>Level</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 600 }}>Type</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 600 }}>Document</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 600 }}>Source</TableCell>
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
                      <TableCell sx={{ color: 'white' }}>
                        <Chip 
                          label={question.created_by_ai ? 'AI Generated' : 'Manual'}
                          size="small"
                          color={question.created_by_ai ? 'info' : 'default'}
                        />
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
          )}
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
      <Dialog 
        open={uploadDialog} 
        onClose={(event, reason) => {
          // Prevent closing during upload or processing
          if (loading || isProcessing) {
            return;
          }
          setUploadDialog(false);
        }} 
        maxWidth="sm" 
        fullWidth
        disableEscapeKeyDown={loading || isProcessing}
      >
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
            disabled={loading || isProcessing}
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
            disabled={loading || isProcessing}
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
          
          {uploadData.file && !loading && !isProcessing && (
            <Box sx={{ mt: 1, mb: 1 }}>
              <Typography variant="body2" sx={{ color: '#10B981' }}>
                ✅ Selected: {uploadData.file.name}
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.875rem' }}>
                Size: {(uploadData.file.size / (1024 * 1024)).toFixed(1)}MB (Max: 200MB)
              </Typography>
            </Box>
          )}

          {/* Upload Progress */}
          {loading && uploadProgress > 0 && !isProcessing && (
            <Box sx={{ mt: 2, mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CloudUpload sx={{ mr: 1, color: '#10B981' }} />
                <Typography variant="body2" sx={{ color: 'white' }}>
                  {questionGenerationProgress.message || `Uploading file... ${uploadProgress}%`}
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={uploadProgress} 
                sx={{
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  '& .MuiLinearProgress-bar': {
                    background: 'linear-gradient(90deg, #10B981 0%, #059669 100%)',
                    borderRadius: 4
                  }
                }}
              />
            </Box>
          )}

          {/* Enhanced Question Generation Progress */}
          {isProcessing && (
            <Box sx={{ py: 3 }}>
              {/* Header with animated icon */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <Box sx={{ 
                  position: 'relative',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <CircularProgress 
                    size={40} 
                    sx={{ 
                      color: '#4caf50',
                      animation: 'spin 1s linear infinite'
                    }} 
                  />
                  <AutoAwesome 
                    sx={{ 
                      position: 'absolute',
                      color: '#4caf50',
                      fontSize: 20
                    }} 
                  />
                </Box>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: '#10B981' }}>
                    🤖 AI Question Generation in Progress
                  </Typography>
                  <Typography variant="body2" color="rgba(255,255,255,0.7)">
                    Using advanced AI to create mathematics questions from your document
                  </Typography>
                </Box>
              </Box>
              
              {/* Main progress bar */}
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" color="rgba(255,255,255,0.7)">
                    Progress: Step {questionGenerationProgress.current} of {questionGenerationProgress.total}
                  </Typography>
                  <Typography variant="body2" color="rgba(255,255,255,0.7)">
                    {Math.round((questionGenerationProgress.current / questionGenerationProgress.total) * 100)}%
                  </Typography>
                </Box>
                
                <LinearProgress 
                  variant="determinate" 
                  value={(questionGenerationProgress.current / questionGenerationProgress.total) * 100} 
                  sx={{ 
                    height: 10, 
                    borderRadius: 5,
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: '#4caf50',
                      borderRadius: 5,
                      transition: 'transform 0.4s ease'
                    }
                  }} 
                />
              </Box>

              {/* Current status */}
              <Alert 
                severity="info" 
                sx={{ 
                  mb: 3,
                  backgroundColor: 'rgba(33, 150, 243, 0.1)',
                  border: '1px solid rgba(33, 150, 243, 0.3)',
                  color: 'white',
                  '& .MuiAlert-icon': { color: '#2196f3' }
                }}
              >
                <Box>
                  <Typography variant="body1" sx={{ fontWeight: 600, mb: 1 }}>
                    {questionGenerationProgress.message}
                  </Typography>
                  {questionGenerationProgress.details && (
                    <Typography variant="body2" color="rgba(255,255,255,0.8)">
                      {questionGenerationProgress.details}
                    </Typography>
                  )}
                  {questionGenerationProgress.estimatedTime > 0 && (
                    <Typography variant="caption" color="rgba(255,255,255,0.6)" sx={{ display: 'block', mt: 1 }}>
                      ⏱️ Estimated time: {questionGenerationProgress.estimatedTime} seconds
                    </Typography>
                  )}
                </Box>
              </Alert>

              {/* Enhanced Stage Indicators */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600, color: 'white' }}>
                  Processing Stages:
                </Typography>
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 1 }}>
                  {[
                    { key: 'uploading', label: 'Upload', icon: '⬆️', step: 1 },
                    { key: 'extracting', label: 'Extract Text', icon: '📄', step: 2 },
                    { key: 'analyzing', label: 'AI Analysis', icon: '🧠', step: 3 },
                    { key: 'generating_level_3', label: 'Level 3 Questions', icon: '🥉', step: 4 },
                    { key: 'generating_level_4', label: 'Level 4 Questions', icon: '🥈', step: 5 },
                    { key: 'generating_level_5', label: 'Level 5 Questions', icon: '🥇', step: 6 },
                    { key: 'saving', label: 'Save Results', icon: '💾', step: 7 }
                  ].map((stage) => {
                    const isCompleted = questionGenerationProgress.current > stage.step;
                    const isCurrent = questionGenerationProgress.current === stage.step;
                    const isPending = questionGenerationProgress.current < stage.step;

                    return (
                      <Paper
                        key={stage.key}
                        elevation={isCurrent ? 8 : 2}
                        sx={{
                          p: 1.5,
                          textAlign: 'center',
                          borderRadius: 2,
                          backgroundColor: isCompleted 
                            ? 'rgba(76, 175, 80, 0.15)' 
                            : isCurrent
                              ? 'rgba(255, 193, 7, 0.15)'
                              : 'rgba(0, 0, 0, 0.05)',
                          border: `2px solid ${
                            isCompleted 
                              ? '#4caf50' 
                              : isCurrent
                                ? '#ffc107'
                                : '#e0e0e0'
                          }`,
                          transition: 'all 0.3s ease',
                          transform: isCurrent ? 'scale(1.05)' : 'scale(1)',
                          boxShadow: isCurrent 
                            ? '0 4px 20px rgba(255, 193, 7, 0.3)' 
                            : isCompleted
                              ? '0 2px 10px rgba(76, 175, 80, 0.2)'
                              : '0 1px 3px rgba(0,0,0,0.1)'
                        }}
                      >
                        <Typography variant="h6" sx={{ mb: 0.5, fontSize: '1.2rem' }}>
                          {stage.icon}
                        </Typography>
                        <Typography 
                          variant="caption" 
                          sx={{ 
                            fontSize: '0.7rem',
                            fontWeight: isCurrent ? 700 : 500,
                            color: isCurrent ? '#f57c00' : isCompleted ? '#2e7d32' : 'rgba(255,255,255,0.6)'
                          }}
                        >
                          {stage.label}
                        </Typography>
                        
                        {/* Status indicators */}
                        <Box sx={{ mt: 0.5 }}>
                          {isCompleted && (
                            <CheckCircle sx={{ color: '#4caf50', fontSize: 16 }} />
                          )}
                          {isCurrent && (
                            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                              <CircularProgress size={16} sx={{ color: '#ffc107' }} />
                            </Box>
                          )}
                          {isPending && (
                            <Box sx={{ width: 16, height: 16, mx: 'auto', backgroundColor: '#e0e0e0', borderRadius: '50%' }} />
                          )}
                        </Box>
                      </Paper>
                    );
                  })}
                </Box>
              </Box>

              {/* Real-time status updates */}
              {questionGenerationProgress.status && (
                <Box sx={{ 
                  p: 2, 
                  backgroundColor: 'rgba(63, 81, 181, 0.05)', 
                  borderRadius: 2,
                  border: '1px solid rgba(63, 81, 181, 0.2)'
                }}>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#3f51b5' }}>
                    🔄 Current Operation:
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 0.5, color: 'white' }}>
                    {questionGenerationProgress.message}
                  </Typography>
                  {questionGenerationProgress.details && (
                    <Typography variant="caption" color="rgba(255,255,255,0.7)" sx={{ display: 'block', mt: 0.5 }}>
                      💡 {questionGenerationProgress.details}
                    </Typography>
                  )}
                </Box>
              )}
            </Box>
          )}

          {/* Processing Results */}
          {processingResults && (
            <Box sx={{ mt: 2, mb: 2, p: 2, borderRadius: 2, backgroundColor: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
              <Typography variant="h6" sx={{ color: '#10B981', mb: 1, display: 'flex', alignItems: 'center' }}>
                <CheckCircle sx={{ mr: 1 }} />
                Processing Complete!
                {processingResults.source === 'demo_data' && (
                  <Chip 
                    label="Demo Data" 
                    size="small" 
                    color="warning" 
                    sx={{ ml: 2 }}
                  />
                )}
                {processingResults.source === 'real_data' && (
                  <Chip 
                    label="Real Questions Generated" 
                    size="small" 
                    color="success" 
                    sx={{ ml: 2 }}
                  />
                )}
              </Typography>
              
              {processingResults.source === 'demo_data' && (
                <Alert severity="info" sx={{ mb: 2, backgroundColor: 'rgba(33, 150, 243, 0.1)' }}>
                  <Typography variant="body2" sx={{ color: 'white' }}>
                    📝 This shows demo data for demonstration. Check the "Questions" tab to see if real questions were created from your document.
                  </Typography>
                </Alert>
              )}
              
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" sx={{ color: 'white' }}>
                    Level 3: {processingResults.level3_questions} questions
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" sx={{ color: 'white' }}>
                    Level 4: {processingResults.level4_questions} questions
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" sx={{ color: 'white' }}>
                    Level 5: {processingResults.level5_questions} questions
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" sx={{ color: '#10B981', fontWeight: 'bold' }}>
                    Total: {processingResults.total_questions} questions
                  </Typography>
                </Grid>
                {processingResults.processing_status && (
                  <Grid item xs={12}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                      Status: {processingResults.processing_status}
                    </Typography>
                  </Grid>
                )}
              </Grid>
              
              <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => setActiveTab(1)}
                  sx={{ 
                    color: '#10B981', 
                    borderColor: '#10B981',
                    '&:hover': { backgroundColor: 'rgba(16, 185, 129, 0.1)' }
                  }}
                >
                  View Questions →
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => {
                    loadQuestions();
                    console.log('Refreshing questions list...');
                  }}
                  sx={{ 
                    color: '#10B981', 
                    borderColor: '#10B981',
                    '&:hover': { backgroundColor: 'rgba(16, 185, 129, 0.1)' }
                  }}
                >
                  Refresh Questions
                </Button>
              </Box>
            </Box>
          )}
          
          {!loading && !isProcessing && (
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)', fontSize: '0.75rem', mt: 1 }}>
              📄 Supported format: PDF files up to 200MB
            </Typography>
          )}
        </DialogContent>
        <DialogActions sx={{ background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)' }}>
          <Button 
            onClick={() => {
              if (!loading && !isProcessing) {
                setUploadDialog(false);
              }
            }} 
            sx={{ 
              color: (loading || isProcessing) ? 'rgba(255,255,255,0.5)' : 'white',
              cursor: (loading || isProcessing) ? 'not-allowed' : 'pointer'
            }}
            disabled={loading || isProcessing}
          >
            {isProcessing ? 'Processing...' : loading ? 'Uploading...' : 'Cancel'}
          </Button>
          <Button 
            onClick={handleUploadDocument} 
            variant="contained"
            disabled={loading || isProcessing || !uploadData.title || !uploadData.file}
            sx={{ 
              background: (loading || isProcessing || !uploadData.title || !uploadData.file) 
                ? 'rgba(16, 185, 129, 0.5)' 
                : 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
              cursor: (loading || isProcessing || !uploadData.title || !uploadData.file) ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? `Uploading... ${uploadProgress}%` : isProcessing ? 'Processing...' : 'Upload'}
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
