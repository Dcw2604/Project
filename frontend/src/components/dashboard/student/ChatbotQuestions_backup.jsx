import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../../hooks/useAuth';
import { 
    Box, 
    TextField, 
    IconButton, 
    Paper, 
    Typography, 
    CircularProgress,
    styled,
    Button,
    Chip,
    List,
    ListItem,
    ListItemText,
    Divider,
    Alert,
    LinearProgress,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    FormControlLabel,
    Switch,
    Fab
} from '@mui/material';
import { 
    Send as SendIcon,
    AttachFile as AttachFileIcon,
    Description as DescriptionIcon,
    Clear as ClearIcon,
    History as HistoryIcon,
    Memory as MemoryIcon,
    AutoAwesome as AutoAwesomeIcon,
    Fullscreen as FullscreenIcon,
    FullscreenExit as FullscreenExitIcon,
    KeyboardArrowUp as KeyboardArrowUpIcon,
    KeyboardArrowDown as KeyboardArrowDownIcon
} from '@mui/icons-material';

const MessageContainer = styled(Box)(({ theme }) => ({
    display: 'flex',
    marginBottom: theme.spacing(2),
    justifyContent: 'flex-start',
    '&.user': {
        justifyContent: 'flex-end'
    }
}));

const MessageBubble = styled(Paper)(({ theme, variant }) => ({
    padding: theme.spacing(3),
    maxWidth: '80%',
    borderRadius: theme.spacing(3),
    boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
    backdropFilter: 'blur(20px)',
    border: '1px solid rgba(255,255,255,0.3)',
    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
    position: 'relative',
    overflow: 'hidden',
    '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        zIndex: -1,
        opacity: 0,
        transition: 'opacity 0.3s ease',
    },
    '&:hover': {
        transform: 'translateY(-4px) scale(1.02)',
        boxShadow: '0 16px 48px rgba(0,0,0,0.25)',
        '&::before': {
            opacity: 1,
        }
    },
    ...(variant === 'user' && {
        background: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`,
        color: 'white',
        border: `1px solid rgba(255,255,255,0.4)`,
        boxShadow: '0 8px 32px rgba(102, 126, 234, 0.3)',
        '&:hover': {
            boxShadow: '0 16px 48px rgba(102, 126, 234, 0.4)',
        }
    }),
    ...(variant === 'error' && {
        background: `linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)`,
        color: 'white',
        border: `1px solid rgba(255,255,255,0.4)`,
        boxShadow: '0 8px 32px rgba(255, 107, 107, 0.3)',
    }),
    ...(variant === 'document' && {
        background: `linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%)`,
        color: 'white',
        border: `1px solid rgba(255,255,255,0.4)`,
        boxShadow: '0 8px 32px rgba(78, 205, 196, 0.3)',
    }),
    ...(variant === 'assistant' && {
        background: `rgba(255, 255, 255, 0.95)`,
        color: theme.palette.text.primary,
        border: `1px solid rgba(255,255,255,0.5)`,
        boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
        backdropFilter: 'blur(30px)',
    })
}));

const ChatContainer = styled(Box)(({ theme }) => ({
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 1000,
    background: `linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)`,
    overflow: 'hidden',
    '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(20px)',
        zIndex: -1
    }
}));

const MessagesArea = styled(Box)(({ theme }) => ({
    flexGrow: 1,
    overflow: 'auto',
    overflowY: 'scroll',
    height: 'calc(100vh - 200px)', // Account for header and input area
    padding: theme.spacing(3),
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(20px)',
    display: 'flex',
    flexDirection: 'column',
    position: 'relative',
    // Smooth scrolling behavior
    scrollBehavior: 'smooth',
    WebkitOverflowScrolling: 'touch',
    overscrollBehavior: 'contain',
    // Enhanced scrollbar styling
    '&::-webkit-scrollbar': {
        width: '14px',
        background: 'transparent',
    },
    '&::-webkit-scrollbar-track': {
        background: 'rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        margin: '8px',
        boxShadow: 'inset 0 0 6px rgba(0,0,0,0.1)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
    },
    '&::-webkit-scrollbar-thumb': {
        background: `linear-gradient(180deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.5))`,
        borderRadius: '12px',
        border: `2px solid transparent`,
        backgroundClip: 'content-box',
        boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
        transition: 'all 0.3s ease',
        '&:hover': {
            background: `linear-gradient(180deg, rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.7))`,
            transform: 'scale(1.05)',
            boxShadow: '0 6px 12px rgba(0,0,0,0.4)',
        },
        '&:active': {
            background: 'rgba(255, 255, 255, 0.8)',
        }
    },
    // Firefox scrollbar styling
    scrollbarWidth: 'thin',
    scrollbarColor: `rgba(255, 255, 255, 0.5) rgba(255, 255, 255, 0.1)`,
    // Mobile responsive improvements
    [theme.breakpoints.down('sm')]: {
        padding: theme.spacing(2),
        height: 'calc(100vh - 220px)',
        '&::-webkit-scrollbar': {
            width: '10px',
        }
    }
}));

const InputArea = styled(Paper)(({ theme }) => ({
    padding: theme.spacing(3),
    borderTop: 'none',
    background: 'rgba(255, 255, 255, 0.15)',
    backdropFilter: 'blur(30px)',
    position: 'sticky',
    bottom: 0,
    zIndex: 1000,
    boxShadow: '0 -8px 32px rgba(0,0,0,0.15)',
    borderRadius: '30px 30px 0 0',
    margin: 0,
    border: '1px solid rgba(255, 255, 255, 0.3)',
    borderBottom: 'none',
    // Mobile responsive
    [theme.breakpoints.down('sm')]: {
        padding: theme.spacing(2),
        borderRadius: '20px 20px 0 0',
    }
}));

const DocumentChip = styled(Chip)(({ theme }) => ({
    margin: theme.spacing(0.5),
    backgroundColor: theme.palette.info.light
}));

const ChatbotQuestions = () => {
    // Load messages from localStorage on component mount
    const [messages, setMessages] = useState(() => {
        const savedMessages = localStorage.getItem('chatbot_messages');
        return savedMessages ? JSON.parse(savedMessages) : [];
    });
    const [newQuestion, setNewQuestion] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [uploadedDocuments, setUploadedDocuments] = useState([]);
    const [selectedDocuments, setSelectedDocuments] = useState([]);
    const [isUploading, setIsUploading] = useState(false);
    const [showDocuments, setShowDocuments] = useState(false);
    const [useRAG, setUseRAG] = useState(true);
    const [showScrollToTop, setShowScrollToTop] = useState(false);
    const [showScrollToBottom, setShowScrollToBottom] = useState(false);
    const messagesEndRef = useRef(null);
    const messagesAreaRef = useRef(null);
    const fileInputRef = useRef(null);
    const { authToken } = useAuth();

    // Save messages to localStorage whenever messages change
    useEffect(() => {
        localStorage.setItem('chatbot_messages', JSON.stringify(messages));
    }, [messages]);

    // Enhanced scroll functions with better mobile support
    const scrollToBottom = () => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ 
                behavior: "smooth",
                block: "end",
                inline: "nearest"
            });
        }
    };

    // Smooth scroll to top for easy navigation
    const scrollToTop = () => {
        if (messagesAreaRef.current) {
            messagesAreaRef.current.scrollTo({ 
                top: 0, 
                behavior: 'smooth' 
            });
        }
    };

    // Quick scroll to bottom (instant for new messages)
    const quickScrollToBottom = () => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView(false);
        }
    };

    // Enhanced scroll detection for better UX
    useEffect(() => {
        const handleScroll = () => {
            if (messagesAreaRef.current) {
                const { scrollTop, scrollHeight, clientHeight } = messagesAreaRef.current;
                const scrollPercent = scrollTop / (scrollHeight - clientHeight);
                
                // Show scroll to top if user has scrolled down more than 20%
                setShowScrollToTop(scrollPercent > 0.2);
                
                // Show scroll to bottom if user is not at the bottom (less than 95%)
                setShowScrollToBottom(scrollPercent < 0.95);
            }
        };

        const messagesArea = messagesAreaRef.current;
        if (messagesArea) {
            messagesArea.addEventListener('scroll', handleScroll);
            // Initial check
            handleScroll();
            
            return () => {
                messagesArea.removeEventListener('scroll', handleScroll);
            };
        }
    }, [messages]);

    useEffect(() => {
        // Auto-scroll to bottom for new messages, but only if user was already near bottom
        const messagesArea = messagesAreaRef.current;
        if (messagesArea && messages.length > 0) {
            const { scrollTop, scrollHeight, clientHeight } = messagesArea;
            const scrollPercent = scrollTop / (scrollHeight - clientHeight);
            
            // If user is near bottom (within 90%), auto-scroll to new message
            if (scrollPercent > 0.9 || messages.length === 1) {
                setTimeout(quickScrollToBottom, 100); // Small delay for DOM update
            }
        }
    }, [messages]);

    // Load user's documents and chat history on component mount
    useEffect(() => {
        loadUserDocuments();
        loadChatHistory();
    }, []);

    const loadUserDocuments = async () => {
        try {
            const headers = {
                'Content-Type': 'application/json',
            };
            
            if (authToken) {
                headers['Authorization'] = `Token ${authToken}`;
            }

            const endpoint = useRAG ? 'rag_documents' : 'documents';
            const response = await fetch(`http://127.0.0.1:8000/api/${endpoint}/`, {
                method: 'GET',
                headers,
            });

            if (response.ok) {
                const data = await response.json();
                setUploadedDocuments(data.documents || []);
            } else if (response.status === 403 || response.status === 401) {
                console.log('Authentication issue loading documents');
                // Don't show error to user for document loading
                setUploadedDocuments([]);
            }
        } catch (error) {
            console.error('Error loading documents:', error);
            setUploadedDocuments([]);
        }
    };

    const loadChatHistory = async () => {
        try {
            const headers = {
                'Content-Type': 'application/json',
            };
            
            if (authToken) {
                headers['Authorization'] = `Token ${authToken}`;
            }

            const response = await fetch(`http://127.0.0.1:8000/api/chat_history/?limit=20`, {
                method: 'GET',
                headers,
            });

            if (response.ok) {
                const data = await response.json();
                
                // Convert backend chat history to frontend message format
                const backendMessages = data.chats || [];
                const convertedMessages = backendMessages.map(chat => [
                    {
                        type: 'user',
                        content: chat.question,
                        timestamp: chat.created_at
                    },
                    {
                        type: 'assistant',
                        content: chat.answer,
                        timestamp: chat.created_at,
                        source: chat.topic,
                        chatId: chat.id
                    }
                ]).flat();

                // Merge with any existing localStorage messages (avoid duplicates)
                const savedMessages = JSON.parse(localStorage.getItem('chatbot_messages') || '[]');
                const existingChatIds = savedMessages
                    .filter(msg => msg.chatId)
                    .map(msg => msg.chatId);
                
                const newMessages = convertedMessages.filter(msg => 
                    !msg.chatId || !existingChatIds.includes(msg.chatId)
                );

                const allMessages = [...savedMessages, ...newMessages];
                setMessages(allMessages);
                localStorage.setItem('chatbot_messages', JSON.stringify(allMessages));
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
            // Fallback to localStorage only
            const savedMessages = JSON.parse(localStorage.getItem('chatbot_messages') || '[]');
            setMessages(savedMessages);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!newQuestion.trim() || isLoading) return;

        // Add user message immediately for better UX
        const userMessage = {
            type: 'user',
            content: newQuestion,
            timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, userMessage]);

        // Add processing indicator if documents are selected
        let processingMessage = null;
        if (selectedDocuments.length > 0) {
            processingMessage = {
                type: 'assistant',
                content: `🔍 Searching through ${selectedDocuments.length} document${selectedDocuments.length > 1 ? 's' : ''} for relevant information...`,
                timestamp: new Date().toISOString(),
                isProcessing: true
            };
            setMessages(prev => [...prev, processingMessage]);
        }

        try {
            setIsLoading(true);
            const headers = {
                'Content-Type': 'application/json',
            };
            
            if (authToken) {
                headers['Authorization'] = `Token ${authToken}`;
            }

            // Choose endpoint based on RAG mode
            const endpoint = useRAG ? 'rag_chat' : 'chat_interaction';

            // Prepare request data
            const requestData = { 
                question: newQuestion,
                document_ids: selectedDocuments
            };

            console.log('Sending request:', {
                endpoint,
                selectedDocuments,
                documentsCount: uploadedDocuments.length,
                question: newQuestion.substring(0, 50) + '...'
            });
            
            const response = await fetch(`http://127.0.0.1:8000/api/${endpoint}/`, {
                method: 'POST',
                headers,
                body: JSON.stringify(requestData),
            });

            if (!response.ok) {
                if (response.status === 403 || response.status === 401) {
                    // Token expired or unauthorized
                    setMessages(prev => {
                        const filteredMessages = prev.filter(msg => !msg.isProcessing);
                        return [...filteredMessages, {
                            type: 'error',
                            content: 'Authentication expired. Please refresh the page and log in again.',
                            timestamp: new Date().toISOString()
                        }];
                    });
                    return;
                }
                throw new Error(`Network response was not ok: ${response.status}`);
            }

            const data = await response.json();
            
            console.log('Received response:', {
                source: data.source,
                documentsUsed: data.documents_used,
                hasAnswer: !!data.answer
            });
            
            // Create the bot response message
            const botMessage = {
                type: data.source === 'document_rag' || data.source === 'documents' ? 'document' : 'assistant',
                content: data.answer,
                timestamp: new Date().toISOString(),
                source: data.source,
                documentsUsed: data.documents_used || [],
                processingInfo: data.processing_info,
                chatId: data.chat_id // Include chatId for consistency
            };

            // Replace processing message with actual response, or just add the response
            setMessages(prev => {
                // Remove any processing messages and add the final response
                const filteredMessages = prev.filter(msg => !msg.isProcessing);
                return [...filteredMessages, botMessage];
            });
            
            setNewQuestion('');

        } catch (error) {
            console.error('Error:', error);
            // Remove processing message and add error message
            setMessages(prev => {
                const filteredMessages = prev.filter(msg => !msg.isProcessing);
                return [...filteredMessages, {
                    type: 'error',
                    content: 'Sorry, there was an error processing your question. Please try again.',
                    timestamp: new Date().toISOString()
                }];
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setIsUploading(true);
        try {
            const formData = new FormData();
            formData.append('document', file);
            formData.append('title', file.name);

            const headers = {};
            if (authToken) {
                headers['Authorization'] = `Token ${authToken}`;
            }

            const response = await fetch('http://127.0.0.1:8000/api/upload_document/', {
                method: 'POST',
                headers,
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                
                // Add upload confirmation message
                setMessages(prev => [...prev, {
                    type: 'document',
                    content: `✅ Document "${file.name}" uploaded and ready! Now you can ask questions about it.`,
                    timestamp: new Date().toISOString(),
                    processingInfo: data.processing_info
                }]);

                // Reload documents list and auto-select the new document
                await loadUserDocuments();
                
                // Auto-select the newly uploaded document
                if (data.document_id) {
                    setSelectedDocuments(prev => {
                        const docId = data.document_id.toString();
                        if (!prev.includes(docId)) {
                            return [...prev, docId];
                        }
                        return prev;
                    });
                }
            } else {
                throw new Error('Upload failed');
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            setMessages(prev => [...prev, {
                type: 'error',
                content: 'Failed to upload document. Please try again.',
                timestamp: new Date().toISOString()
            }]);
        } finally {
            setIsUploading(false);
        }
    };

    const handleDocumentSelect = (documentId) => {
        setSelectedDocuments(prev => {
            if (prev.includes(documentId)) {
                return prev.filter(id => id !== documentId);
            } else {
                return [...prev, documentId];
            }
        });
    };

    const clearMemory = async () => {
        try {
            const headers = {
                'Content-Type': 'application/json',
            };
            
            if (authToken) {
                headers['Authorization'] = `Token ${authToken}`;
            }

            const endpoint = useRAG ? 'rag_clear_memory' : 'clear_memory';
            const response = await fetch(`http://127.0.0.1:8000/api/${endpoint}/`, {
                method: 'DELETE',
                headers,
            });

            if (response.ok) {
                const data = await response.json();
                
                // Create success message with details
                let successMessage = 'Memory cleared successfully! Starting fresh!';
                if (data.details) {
                    const { documents_deleted, files_deleted } = data.details;
                    if (documents_deleted > 0 || files_deleted > 0) {
                        successMessage += `\n\n📁 Deleted ${documents_deleted} document${documents_deleted !== 1 ? 's' : ''} and ${files_deleted} file${files_deleted !== 1 ? 's' : ''}.`;
                    }
                }
                
                // Show warnings if any
                if (data.warnings && data.warnings.length > 0) {
                    successMessage += '\n\n⚠️ Some files could not be deleted:\n' + data.warnings.join('\n');
                }
                
                setMessages(prev => [...prev, {
                    type: 'bot',
                    content: successMessage,
                    timestamp: new Date().toISOString()
                }]);
                
                // Clear uploaded documents from state since they were deleted
                setUploadedDocuments([]);
                setSelectedDocuments([]);
                
                // Refresh documents list
                loadUserDocuments();
            } else {
                const errorData = await response.json();
                setMessages(prev => [...prev, {
                    type: 'bot',
                    content: `❌ Failed to clear memory: ${errorData.error || 'Unknown error'}`,
                    timestamp: new Date().toISOString()
                }]);
            }
        } catch (error) {
            console.error('Error clearing memory:', error);
            setMessages(prev => [...prev, {
                type: 'bot',
                content: `❌ Error clearing memory: ${error.message}`,
                timestamp: new Date().toISOString()
            }]);
        }
    };

    const renderMessage = (message, index) => {
        return (
            <MessageContainer key={index} className={message.type === 'user' ? 'user' : ''}>
                <MessageBubble 
                    variant={message.type} 
                    elevation={1}
                >
                    <Typography>{message.content}</Typography>
                    
                    {/* Show document info for document-based responses */}
                    {message.documentsUsed && message.documentsUsed.length > 0 && (
                        <Box sx={{ mt: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                                Sources:
                            </Typography>
                            {message.documentsUsed.map((doc, idx) => (
                                <DocumentChip 
                                    key={idx}
                                    label={`${doc.title} (${doc.type})`}
                                    size="small"
                                    icon={<DescriptionIcon />}
                                />
                            ))}
                        </Box>
                    )}

                    {/* Show processing info */}
                    {message.processingInfo && (
                        <Box sx={{ mt: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                                Processed: {message.processingInfo.pages} pages, 
                                {message.processingInfo.text_length} characters
                            </Typography>
                        </Box>
                    )}

                    {/* Show source badge */}
                    {message.source && (
                        <Box sx={{ mt: 1 }}>
                            <Chip 
                                label={message.source} 
                                size="small" 
                                variant="outlined"
                                icon={message.source === 'documents' ? <DescriptionIcon /> : <AutoAwesomeIcon />}
                            />
                        </Box>
                    )}
                </MessageBubble>
            </MessageContainer>
        );
    };

    return (
        <ChatContainer>
            {/* Top Navigation Bar for Tabs */}
            <Box 
                sx={{ 
                    height: '70px',
                    background: 'linear-gradient(135deg, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0.15) 100%)',
                    backdropFilter: 'blur(30px)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    px: 4,
                    boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
                    border: '1px solid rgba(255,255,255,0.3)',
                    borderBottom: '1px solid rgba(255,255,255,0.2)',
                    zIndex: 1100,
                    position: 'relative'
                }}
            >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <AutoAwesomeIcon sx={{ fontSize: 32, color: 'white', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))' }} />
                    <Typography 
                        variant="h5" 
                        sx={{ 
                            color: 'white',
                            fontWeight: 700,
                            textShadow: '0 2px 8px rgba(0,0,0,0.4)',
                            letterSpacing: '0.5px'
                        }}
                    >
                        Enhanced AI Chatbot
                    </Typography>
                    <Chip 
                        label={useRAG ? 'RAG Mode' : 'Standard Mode'}
                        size="small"
                        sx={{ 
                            backgroundColor: useRAG ? 'rgba(76, 205, 50, 0.8)' : 'rgba(255, 193, 7, 0.8)',
                            color: 'white',
                            fontWeight: 600,
                            backdropFilter: 'blur(10px)',
                            border: '1px solid rgba(255,255,255,0.3)'
                        }}
                    />
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <FormControlLabel
                        control={
                            <Switch
                                checked={useRAG}
                                onChange={(e) => setUseRAG(e.target.checked)}
                                sx={{
                                    '& .MuiSwitch-thumb': {
                                        backgroundColor: 'white',
                                        boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
                                    },
                                    '& .MuiSwitch-track': {
                                        backgroundColor: 'rgba(255,255,255,0.3)',
                                        border: '1px solid rgba(255,255,255,0.5)'
                                    }
                                }}
                            />
                        }
                        label={<Typography sx={{ color: 'white', fontWeight: 500 }}>RAG Mode</Typography>}
                    />
                    <Button
                        startIcon={<HistoryIcon />}
                        onClick={() => setShowDocuments(!showDocuments)}
                        variant="outlined"
                        size="small"
                        sx={{
                            color: 'white',
                            borderColor: 'rgba(255,255,255,0.5)',
                            backgroundColor: 'rgba(255,255,255,0.1)',
                            backdropFilter: 'blur(10px)',
                            '&:hover': {
                                backgroundColor: 'rgba(255,255,255,0.2)',
                                borderColor: 'rgba(255,255,255,0.8)'
                            }
                        }}
                    >
                        Documents ({uploadedDocuments.length})
                    </Button>
                    <Button
                        startIcon={<MemoryIcon />}
                        onClick={clearMemory}
                        variant="outlined"
                        size="small"
                        sx={{
                            color: 'white',
                            borderColor: 'rgba(255,152,0,0.7)',
                            backgroundColor: 'rgba(255,152,0,0.1)',
                            backdropFilter: 'blur(10px)',
                            '&:hover': {
                                backgroundColor: 'rgba(255,152,0,0.2)',
                                borderColor: 'rgba(255,152,0,1)'
                            }
                        }}
                        title="Clear conversation memory and delete all uploaded files"
                    >
                        Clear Memory & Files
                    </Button>
                    <Button
                        startIcon={<ClearIcon />}
                        onClick={() => {
                            setMessages([]);
                            localStorage.removeItem('chatbot_messages');
                        }}
                        variant="outlined"
                        size="small"
                        sx={{
                            color: 'white',
                            borderColor: 'rgba(244,67,54,0.7)',
                            backgroundColor: 'rgba(244,67,54,0.1)',
                            backdropFilter: 'blur(10px)',
                            '&:hover': {
                                backgroundColor: 'rgba(244,67,54,0.2)',
                                borderColor: 'rgba(244,67,54,1)'
                            }
                        }}
                    >
                        Clear Chat
                    </Button>
                </Box>
            </Box>

            {/* Document list and selection */}
            {showDocuments && (
                <Paper 
                    sx={{ 
                        mx: 2, 
                        mt: 1, 
                        mb: 1,
                        background: 'rgba(255, 255, 255, 0.15)',
                        backdropFilter: 'blur(20px)',
                        border: '1px solid rgba(255, 255, 255, 0.3)',
                        borderRadius: 3,
                        maxHeight: 200, 
                        overflow: 'auto',
                        boxShadow: '0 8px 32px rgba(0,0,0,0.15)'
                    }}
                >
                    <List dense>
                        {uploadedDocuments.map((doc) => (
                            <ListItem 
                                key={doc.id} 
                                button 
                                onClick={() => handleDocumentSelect(doc.id.toString())}
                                selected={selectedDocuments.includes(doc.id.toString())}
                                sx={{
                                    color: 'white',
                                    '&:hover': {
                                        backgroundColor: 'rgba(255, 255, 255, 0.1)'
                                    },
                                    '&.Mui-selected': {
                                        backgroundColor: 'rgba(255, 255, 255, 0.2)',
                                        '&:hover': {
                                            backgroundColor: 'rgba(255, 255, 255, 0.25)'
                                        }
                                    }
                                }}
                            >
                                <ListItemText
                                    primary={
                                        <Typography sx={{ color: 'white', fontWeight: 500 }}>
                                            {doc.title}
                                        </Typography>
                                    }
                                    secondary={
                                        <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.8rem' }}>
                                            {doc.document_type} • {doc.pages} pages • {doc.text_preview.slice(0, 50)}...
                                        </Typography>
                                    }
                                />
                            </ListItem>
                        ))}
                        {uploadedDocuments.length === 0 && (
                            <ListItem>
                                <ListItemText
                                    primary={
                                        <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)', textAlign: 'center' }}>
                                            No documents uploaded yet
                                        </Typography>
                                    }
                                />
                            </ListItem>
                        )}
                    </List>
                </Paper>
            )}

            {/* Selected documents display */}
            {selectedDocuments.length > 0 && (
                <Box sx={{ mx: 2, mb: 1 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.8)', fontWeight: 500 }}>
                        Selected documents:
                    </Typography>
                    <Box sx={{ mt: 0.5 }}>
                        {selectedDocuments.map(docId => {
                            const doc = uploadedDocuments.find(d => d.id.toString() === docId);
                            return doc ? (
                                <Chip 
                                    key={docId}
                                    label={doc.title}
                                    onDelete={() => handleDocumentSelect(docId)}
                                    icon={<DescriptionIcon />}
                                    size="small"
                                    sx={{ 
                                        margin: 0.5,
                                        backgroundColor: 'rgba(78, 205, 196, 0.8)',
                                        color: 'white',
                                        backdropFilter: 'blur(10px)',
                                        border: '1px solid rgba(255,255,255,0.3)',
                                        '& .MuiChip-deleteIcon': {
                                            color: 'rgba(255, 255, 255, 0.8)'
                                        }
                                    }}
                                />
                            ) : null;
                        })}
                    </Box>
                </Box>
            )}

            {/* Chat messages area */}
            <MessagesArea ref={messagesAreaRef}>
                {messages.length === 0 && (
                    <Box 
                        sx={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'center', 
                            height: '100%',
                            opacity: 0.7,
                            flexDirection: 'column',
                            textAlign: 'center'
                        }}
                    >
                        <AutoAwesomeIcon sx={{ fontSize: 80, color: 'rgba(255, 255, 255, 0.5)', mb: 2 }} />
                        <Typography 
                            variant="h5" 
                            sx={{ 
                                color: 'rgba(255, 255, 255, 0.8)', 
                                mb: 1, 
                                fontWeight: 600 
                            }}
                        >
                            Welcome to Enhanced AI Chat
                        </Typography>
                        <Typography 
                            variant="body1" 
                            sx={{ 
                                color: 'rgba(255, 255, 255, 0.6)', 
                                maxWidth: 500 
                            }}
                        >
                            Start a conversation or upload documents to ask questions about specific content.
                            {useRAG ? ' RAG mode is enabled for enhanced document understanding.' : ' Switch to RAG mode for document-based Q&A.'}
                        </Typography>
                    </Box>
                )}

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {messages.map((message, index) => renderMessage(message, index))}
                </Box>
            </MessagesArea>

            {/* Scroll buttons */}
            {showScrollToTop && (
                <Fab
                    size="small"
                    sx={{ 
                        position: 'fixed', 
                        bottom: 120, 
                        right: 30, 
                        zIndex: 1200,
                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                        backdropFilter: 'blur(10px)',
                        border: '1px solid rgba(255, 255, 255, 0.3)',
                        boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
                        '&:hover': {
                            backgroundColor: 'rgba(255, 255, 255, 1)'
                        }
                    }}
                    onClick={scrollToTop}
                >
                    <KeyboardArrowUpIcon />
                </Fab>
            )}

            {showScrollToBottom && (
                <Fab
                    size="small"
                    sx={{ 
                        position: 'fixed', 
                        bottom: 170, 
                        right: 30, 
                        zIndex: 1200,
                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                        backdropFilter: 'blur(10px)',
                        border: '1px solid rgba(255, 255, 255, 0.3)',
                        boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
                        '&:hover': {
                            backgroundColor: 'rgba(255, 255, 255, 1)'
                        }
                    }}
                    onClick={scrollToBottom}
                >
                    <KeyboardArrowDownIcon />
                </Fab>
            )}

            {/* Loading indicator */}
            {isUploading && (
                <Box sx={{ position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', zIndex: 2000 }}>
                    <Paper 
                        sx={{ 
                            p: 3, 
                            display: 'flex', 
                            alignItems: 'center', 
                            gap: 2,
                            background: 'rgba(255, 255, 255, 0.95)',
                            backdropFilter: 'blur(20px)',
                            border: '1px solid rgba(255, 255, 255, 0.3)',
                            borderRadius: 3,
                            boxShadow: '0 16px 48px rgba(0,0,0,0.2)'
                        }}
                    >
                        <CircularProgress size={24} />
                        <Typography>Uploading document...</Typography>
                    </Paper>
                </Box>
            )}

            {/* Input area */}
            <InputArea>
                <Box 
                    component="form" 
                    onSubmit={handleSubmit} 
                    sx={{ 
                        display: 'flex',
                        gap: 2,
                        alignItems: 'flex-end' 
                    }}
                >
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileUpload}
                        style={{ display: 'none' }}
                        accept=".pdf,.txt,.doc,.docx"
                    />
                    
                    <IconButton
                        onClick={() => fileInputRef.current?.click()}
                        title="Upload document"
                        size="large"
                        disabled={isUploading}
                        sx={{
                            backgroundColor: 'rgba(255, 255, 255, 0.9)',
                            backdropFilter: 'blur(10px)',
                            border: '1px solid rgba(255, 255, 255, 0.3)',
                            color: '#667eea',
                            '&:hover': {
                                backgroundColor: 'rgba(255, 255, 255, 1)',
                                transform: 'scale(1.05)'
                            }
                        }}
                    >
                        <AttachFileIcon />
                    </IconButton>
                    
                    <TextField
                        fullWidth
                        multiline
                        maxRows={4}
                        value={newQuestion}
                        onChange={(e) => setNewQuestion(e.target.value)}
                        placeholder={selectedDocuments.length > 0 
                            ? `Ask about: ${selectedDocuments.map(id => {
                                const doc = uploadedDocuments.find(d => d.id.toString() === id);
                                return doc ? doc.title : 'document';
                            }).join(', ')}...` 
                            : uploadedDocuments.length > 0 
                                ? "Select documents above or ask general questions..."
                                : "Ask me anything about math, general topics, or upload a document first..."
                        }
                        disabled={isLoading || isUploading}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSubmit(e);
                            }
                        }}
                        variant="outlined"
                        sx={{ 
                            backgroundColor: 'rgba(255, 255, 255, 0.9)',
                            backdropFilter: 'blur(10px)',
                            borderRadius: 3,
                            '& .MuiOutlinedInput-root': {
                                '& fieldset': {
                                    borderColor: 'rgba(255, 255, 255, 0.3)',
                                    borderRadius: 3
                                },
                                '&:hover fieldset': {
                                    borderColor: 'rgba(255, 255, 255, 0.5)'
                                },
                                '&.Mui-focused fieldset': {
                                    borderColor: 'rgba(255, 255, 255, 0.8)'
                                }
                            }
                        }}
                    />

                    <IconButton
                        type="submit"
                        disabled={isLoading || !newQuestion.trim() || isUploading}
                        title="Send message"
                        size="large"
                        sx={{
                            backgroundColor: isLoading || !newQuestion.trim() || isUploading 
                                ? 'rgba(255, 255, 255, 0.5)' 
                                : 'rgba(102, 126, 234, 0.9)',
                            backdropFilter: 'blur(10px)',
                            border: '1px solid rgba(255, 255, 255, 0.3)',
                            color: isLoading || !newQuestion.trim() || isUploading ? 'rgba(0,0,0,0.3)' : 'white',
                            '&:hover': {
                                backgroundColor: isLoading || !newQuestion.trim() || isUploading 
                                    ? 'rgba(255, 255, 255, 0.5)' 
                                    : 'rgba(102, 126, 234, 1)',
                                transform: isLoading || !newQuestion.trim() || isUploading ? 'none' : 'scale(1.05)'
                            }
                        }}
                    >
                        {isLoading ? (
                            <CircularProgress size={24} sx={{ color: 'rgba(0,0,0,0.3)' }} />
                        ) : (
                            <SendIcon />
                        )}
                    </IconButton>
                </Box>
            </InputArea>

            {/* Hidden div for auto-scroll */}
            <div ref={messagesEndRef} />
        </ChatContainer>
    );
                {messages.length === 0 && (
                    <Box 
                        sx={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'center', 
                            height: '100%',
                            opacity: 0.6,
                            flexDirection: 'column',
                            textAlign: 'center'
                        }}
                    >
                        <AutoAwesomeIcon sx={{ fontSize: 48, mb: 2 }} />
                        <Typography variant="h6" color="text.secondary" gutterBottom>
                            Enhanced AI Chatbot with RAG
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            • Upload documents for AI-powered Q&A<br/>
                            • Conversation memory for context<br/>
                            • Math problem solving<br/>
                            • Multi-document search
                        </Typography>
                    </Box>
                )}
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {messages.map((message, index) => renderMessage(message, index))}
                </Box>
                <div ref={messagesEndRef} />
            </MessagesArea>

            {/* Floating Action Buttons for Scroll Navigation */}
            {showScrollToTop && (
                <Fab
                    size="small"
                    color="primary"
                    aria-label="scroll to top"
                    onClick={scrollToTop}
                    sx={{
                        position: 'absolute',
                        bottom: 120,
                        right: 20,
                        zIndex: 1000,
                        opacity: 0.8,
                        transition: 'all 0.3s ease',
                        '&:hover': {
                            opacity: 1,
                            transform: 'scale(1.1)'
                        }
                    }}
                >
                    <KeyboardArrowUpIcon />
                </Fab>
            )}
            
            {showScrollToBottom && messages.length > 3 && (
                <Fab
                    size="small"
                    color="secondary"
                    aria-label="scroll to bottom"
                    onClick={scrollToBottom}
                    sx={{
                        position: 'absolute',
                        bottom: 70,
                        right: 20,
                        zIndex: 1000,
                        opacity: 0.8,
                        transition: 'all 0.3s ease',
                        '&:hover': {
                            opacity: 1,
                            transform: 'scale(1.1)'
                        }
                    }}
                >
                    <KeyboardArrowDownIcon />
                </Fab>
            )}

            {/* Input area */}
            <InputArea elevation={3}>
                {isUploading && (
                    <Box sx={{ mb: 2 }}>
                        <LinearProgress />
                        <Typography variant="caption" color="text.secondary">
                            Uploading and processing document...
                        </Typography>
                    </Box>
                )}

                <Box 
                    component="form" 
                    onSubmit={handleSubmit} 
                    sx={{ 
                        display: 'flex',
                        gap: 2,
                        alignItems: 'flex-end' 
                    }}
                >
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileUpload}
                        style={{ display: 'none' }}
                        accept=".pdf,.txt,.doc,.docx"
                    />
                    
                    <IconButton
                        onClick={() => fileInputRef.current?.click()}
                        color="primary"
                        title="Upload document"
                        size="large"
                        disabled={isUploading}
                    >
                        <AttachFileIcon />
                    </IconButton>
                    
                    <TextField
                        fullWidth
                        multiline
                        maxRows={4}
                        value={newQuestion}
                        onChange={(e) => setNewQuestion(e.target.value)}
                        placeholder={selectedDocuments.length > 0 
                            ? `Ask about: ${selectedDocuments.map(id => {
                                const doc = uploadedDocuments.find(d => d.id.toString() === id);
                                return doc ? doc.title : 'document';
                            }).join(', ')}...` 
                            : uploadedDocuments.length > 0 
                                ? "Select documents above or ask general questions..."
                                : "Ask me anything about math, general topics, or upload a document first..."
                        }
                        disabled={isLoading || isUploading}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSubmit(e);
                            }
                        }}
                        variant="outlined"
                        sx={{ backgroundColor: 'background.paper' }}
                    />

                    <IconButton
                        type="submit"
                        disabled={isLoading || !newQuestion.trim() || isUploading}
                        color="primary"
                        title="Send message"
                        size="large"
                    >
                        {isLoading ? (
                            <CircularProgress size={24} />
                        ) : (
                            <SendIcon />
                        )}
                    </IconButton>
                </Box>
            </InputArea>
        </ChatContainer>
    );
};

export default ChatbotQuestions;