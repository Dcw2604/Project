/**
 * 🎯 Interactive Exam Learning Component with OLAMA Integration
 * 
 * This component implements the improved interactive learning flow:
 * - Students answer questions from exam sessions
 * - Correct answers move to next question immediately
 * - Incorrect answers get OLAMA-generated hints
 * - After max attempts, reveals answer and moves on
 * - Tracks all attempts and provides detailed progress
 */

import React, { useState, useEffect } from 'react';
import { useApi } from '../../../hooks/useApi';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Alert,
  LinearProgress,
  Chip,
  Stack,
  RadioGroup,
  FormControlLabel,
  Radio,
  FormControl,
  FormLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Paper,
  Divider,
  CircularProgress
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Lightbulb,
  ExpandMore,
  Psychology,
  Timer,
  TrendingUp,
  EmojiEvents
} from '@mui/icons-material';

const InteractiveExamLearning = ({ examSessionId, onExamComplete }) => {
  // Core state
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [progress, setProgress] = useState(null);
  const [examCompleted, setExamCompleted] = useState(false);
  
  // Interaction state
  const [lastResponse, setLastResponse] = useState(null);
  const [currentAttempts, setCurrentAttempts] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // UI state
  const [showHintHistory, setShowHintHistory] = useState(false);
  const [startTime, setStartTime] = useState(new Date());

  const { apiCall } = useApi();

  useEffect(() => {
    if (examSessionId) {
      loadExamProgress();
      setStartTime(new Date());
    }
  }, [examSessionId]);

  const loadExamProgress = async () => {
    try {
      setLoading(true);
      const response = await apiCall(`/interactive-exam-progress/${examSessionId}/`, 'GET');
      
      if (response.status === 'success') {
        setProgress(response.progress);
        setCurrentQuestion(response.progress.current_question);
        setCurrentAttempts(response.progress.current_question_attempts || []);
        
        if (response.progress.answered_questions >= response.progress.total_questions) {
          setExamCompleted(true);
          onExamComplete && onExamComplete(response.progress);
        }
      } else {
        setError(response.message || 'Failed to load exam progress');
      }
    } catch (err) {
      setError('Failed to load exam progress');
      console.error('Error loading exam progress:', err);
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!answer.trim()) {
      setError('Please provide an answer');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const timeElapsed = Math.floor((new Date() - startTime) / 1000);
      
      const payload = {
        exam_session_id: examSessionId,
        question_id: currentQuestion.id,
        answer_text: answer.trim(),
        time_taken_seconds: timeElapsed
      };

      const response = await apiCall('/interactive-exam-answers/', 'POST', payload);

      setLastResponse(response);

      if (response.status === 'correct') {
        // ✅ Correct answer - move to next question
        setCurrentQuestion(response.next_question);
        setProgress(response.progress);
        setCurrentAttempts([]);
        setAnswer('');
        
        if (!response.next_question) {
          // Exam completed
          setExamCompleted(true);
          onExamComplete && onExamComplete(response);
        }
        
      } else if (response.status === 'hint') {
        // 💡 Incorrect - show hint and allow retry
        const newAttempt = {
          attempt_number: response.attempt_number,
          answer_text: answer.trim(),
          is_correct: false,
          hint_provided: response.hint,
          submitted_at: new Date().toISOString()
        };
        
        setCurrentAttempts(prev => [...prev, newAttempt]);
        setAnswer(''); // Clear for next attempt
        
      } else if (response.status === 'reveal') {
        // 🔍 Max attempts reached - reveal answer and move on
        const newAttempt = {
          attempt_number: response.attempt_number,
          answer_text: answer.trim(),
          is_correct: false,
          submitted_at: new Date().toISOString()
        };
        
        setCurrentAttempts(prev => [...prev, newAttempt]);
        setCurrentQuestion(response.next_question);
        setProgress(response.progress);
        setCurrentAttempts([]);
        setAnswer('');
        
        if (!response.next_question) {
          // Exam completed
          setExamCompleted(true);
          onExamComplete && onExamComplete(response);
        }
        
      } else if (response.status === 'completed') {
        // 🎉 Exam completed
        setExamCompleted(true);
        onExamComplete && onExamComplete(response);
      }

    } catch (err) {
      setError(err.message || 'Failed to submit answer');
      console.error('Error submitting answer:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAnswerChange = (e) => {
    setAnswer(e.target.value);
    setError('');
  };

  const handleMultipleChoiceAnswer = (option) => {
    setAnswer(option);
    setError('');
  };

  const renderCompletionScreen = () => (
    <Card sx={{ textAlign: 'center', p: 4 }}>
      <CardContent>
        <EmojiEvents sx={{ fontSize: 60, color: 'gold', mb: 2 }} />
        <Typography variant="h4" gutterBottom color="primary">
          Exam Completed!
        </Typography>
        
        {lastResponse && lastResponse.final_score && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Final Results
            </Typography>
            
            <Stack direction="row" spacing={2} justifyContent="center" sx={{ mb: 3 }}>
              <Chip 
                icon={<CheckCircle />}
                label={`${lastResponse.final_score.correct_answers} / ${lastResponse.final_score.total_questions} Correct`}
                color="success"
                size="large"
              />
              <Chip 
                icon={<TrendingUp />}
                label={`${lastResponse.final_score.score_percentage}% Score`}
                color="primary"
                size="large"
              />
              <Chip 
                icon={<Psychology />}
                label={`${lastResponse.final_score.efficiency_score}% Efficiency`}
                color="secondary"
                size="large"
              />
            </Stack>

            <Typography variant="body1" color="text.secondary">
              Total Attempts: {lastResponse.final_score.total_attempts}
            </Typography>
          </Box>
        )}
        
        <Typography variant="body1" sx={{ mt: 2 }}>
          Great job completing the interactive exam! Your answers and progress have been saved.
        </Typography>
      </CardContent>
    </Card>
  );

  const renderProgress = () => {
    if (!progress) return null;

    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">Progress</Typography>
            <Stack direction="row" spacing={1}>
              <Chip 
                label={`${progress.answered_questions} / ${progress.total_questions}`}
                size="small"
              />
              <Chip 
                label={`${progress.progress_percentage}%`}
                color="primary"
                size="small"
              />
              {progress.accuracy_percentage !== undefined && (
                <Chip 
                  label={`${progress.accuracy_percentage}% Accuracy`}
                  color="success"
                  size="small"
                />
              )}
            </Stack>
          </Stack>
          
          <LinearProgress 
            variant="determinate" 
            value={progress.progress_percentage}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </CardContent>
      </Card>
    );
  };

  const renderCurrentQuestion = () => {
    if (!currentQuestion) return null;

    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
            <Chip 
              label={`Question ${progress?.answered_questions + 1 || 1}`}
              color="primary"
              size="small"
            />
            <Chip 
              label={currentQuestion.question_type === 'multiple_choice' ? 'Multiple Choice' : 'Open Ended'}
              variant="outlined"
              size="small"
            />
            {currentAttempts.length > 0 && (
              <Chip 
                label={`Attempt ${currentAttempts.length + 1}`}
                color="warning"
                size="small"
              />
            )}
          </Stack>

          <Typography variant="h6" sx={{ mb: 3 }}>
            {currentQuestion.question_text}
          </Typography>

          {/* Answer Input */}
          {currentQuestion.question_type === 'multiple_choice' ? (
            <FormControl component="fieldset" sx={{ mb: 3 }}>
              <FormLabel component="legend">Choose your answer:</FormLabel>
              <RadioGroup value={answer} onChange={(e) => handleMultipleChoiceAnswer(e.target.value)}>
                {['A', 'B', 'C', 'D'].map(option => {
                  const optionText = currentQuestion[`option_${option.toLowerCase()}`];
                  if (!optionText) return null;
                  
                  return (
                    <FormControlLabel
                      key={option}
                      value={option}
                      control={<Radio />}
                      label={`${option}. ${optionText}`}
                    />
                  );
                })}
              </RadioGroup>
            </FormControl>
          ) : (
            <TextField
              fullWidth
              multiline
              rows={4}
              value={answer}
              onChange={handleAnswerChange}
              placeholder="Type your answer here..."
              variant="outlined"
              sx={{ mb: 3 }}
            />
          )}

          {/* Submit Button */}
          <Button
            variant="contained"
            onClick={submitAnswer}
            disabled={isSubmitting || !answer.trim()}
            fullWidth
            size="large"
            startIcon={isSubmitting ? <CircularProgress size={20} /> : <CheckCircle />}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Answer'}
          </Button>
        </CardContent>
      </Card>
    );
  };

  const renderAttemptHistory = () => {
    if (currentAttempts.length === 0) return null;

    return (
      <Accordion expanded={showHintHistory} onChange={() => setShowHintHistory(!showHintHistory)}>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="h6">
            <Lightbulb sx={{ mr: 1, verticalAlign: 'middle' }} />
            Previous Attempts & Hints ({currentAttempts.length})
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <List>
            {currentAttempts.map((attempt, index) => (
              <React.Fragment key={index}>
                <ListItem sx={{ flexDirection: 'column', alignItems: 'stretch' }}>
                  <Paper sx={{ p: 2, mb: 1, width: '100%' }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                      <Chip 
                        label={`Attempt ${attempt.attempt_number}`}
                        size="small"
                        color="warning"
                      />
                      <Typography variant="caption" color="text.secondary">
                        {new Date(attempt.submitted_at).toLocaleTimeString()}
                      </Typography>
                    </Stack>
                    
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Your Answer:</strong> {attempt.answer_text}
                    </Typography>
                    
                    {attempt.hint_provided && (
                      <Alert 
                        severity="info" 
                        icon={<Lightbulb />}
                        sx={{ mt: 1 }}
                      >
                        <Typography variant="body2">
                          <strong>Hint:</strong> {attempt.hint_provided}
                        </Typography>
                      </Alert>
                    )}
                  </Paper>
                </ListItem>
                {index < currentAttempts.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </AccordionDetails>
      </Accordion>
    );
  };

  const renderResponseFeedback = () => {
    if (!lastResponse) return null;

    const { status, message, correct_answer } = lastResponse;
    
    const getSeverity = () => {
      switch (status) {
        case 'correct': return 'success';
        case 'hint': return 'info';
        case 'reveal': return 'warning';
        case 'completed': return 'success';
        default: return 'info';
      }
    };

    const getIcon = () => {
      switch (status) {
        case 'correct': return <CheckCircle />;
        case 'hint': return <Lightbulb />;
        case 'reveal': return <Cancel />;
        case 'completed': return <EmojiEvents />;
        default: return null;
      }
    };

    return (
      <Alert 
        severity={getSeverity()} 
        icon={getIcon()}
        sx={{ mb: 3 }}
      >
        <Typography variant="body1">
          {message}
        </Typography>
        
        {correct_answer && (
          <Typography variant="body2" sx={{ mt: 1 }}>
            <strong>Correct Answer:</strong> {correct_answer}
          </Typography>
        )}
        
        {status === 'hint' && lastResponse.hint && (
          <Typography variant="body2" sx={{ mt: 1 }}>
            <strong>Hint:</strong> {lastResponse.hint}
          </Typography>
        )}
        
        {lastResponse.attempts_remaining !== undefined && (
          <Typography variant="body2" sx={{ mt: 1 }}>
            Attempts remaining: {lastResponse.attempts_remaining}
          </Typography>
        )}
      </Alert>
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading exam...</Typography>
      </Box>
    );
  }

  if (examCompleted) {
    return renderCompletionScreen();
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 2 }}>
      <Typography variant="h4" gutterBottom>
        <Psychology sx={{ mr: 1, verticalAlign: 'middle' }} />
        Interactive Exam Learning
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {renderProgress()}
      {renderResponseFeedback()}
      {renderCurrentQuestion()}
      {renderAttemptHistory()}
    </Box>
  );
};

export default InteractiveExamLearning;
