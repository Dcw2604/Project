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
    CameraAlt as CameraAltIcon,
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
    height: 'calc(100vh - 80px)', // Account for header height
    display: 'flex',
    flexDirection: 'column',
    position: 'fixed',
    top: '80px', // Start below the header
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
    
    // Image upload states
    const [selectedImage, setSelectedImage] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [isImageProcessing, setIsImageProcessing] = useState(false);
    const messagesEndRef = useRef(null);
    const messagesAreaRef = useRef(null);
    const fileInputRef = useRef(null);
    const imageInputRef = useRef(null);
    const { authToken } = useAuth();

    // Save messages to localStorage whenever messages change
    useEffect(() => {
        localStorage.setItem('chatbot_messages', JSON.stringify(messages));
    }, [messages]);

    // Enhanced scroll functions with better mobile support
    const scrollToBottom = () => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ 
                behavior: 'smooth',
                block: 'nearest' 
            });
        }
    };

    const scrollToTop = () => {
        if (messagesAreaRef.current) {
            messagesAreaRef.current.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
    };

    // Enhanced scroll monitoring with throttling
    useEffect(() => {
        const messagesArea = messagesAreaRef.current;
        if (!messagesArea) return;

        let scrollTimeout;
        const handleScroll = () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                const { scrollTop, scrollHeight, clientHeight } = messagesArea;
                const isAtTop = scrollTop < 100;
                const isAtBottom = scrollTop + clientHeight >= scrollHeight - 100;
                
                setShowScrollToTop(!isAtTop && scrollTop > 200);
                setShowScrollToBottom(!isAtBottom && messages.length > 3);
            }, 16); // ~60fps throttling
        };

        messagesArea.addEventListener('scroll', handleScroll, { passive: true });
        return () => {
            messagesArea.removeEventListener('scroll', handleScroll);
            clearTimeout(scrollTimeout);
        };
    }, [messages.length]);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        const timer = setTimeout(() => {
            scrollToBottom();
        }, 100);
        return () => clearTimeout(timer);
    }, [messages]);

    // Load user documents on component mount
    useEffect(() => {
        loadUserDocuments();
    }, [authToken]);

    const loadUserDocuments = async () => {
        if (!authToken) return;
        
        try {
            const response = await fetch('http://127.0.0.1:8000/api/documents/', {
                headers: {
                    'Authorization': `Token ${authToken}`,
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const data = await response.json();
                setUploadedDocuments(data.documents || []);
            } else {
                console.error('Failed to load documents:', response.status);
            }
        } catch (error) {
            console.error('Error loading documents:', error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if ((!newQuestion.trim() && !selectedImage) || isLoading) return;

        setIsLoading(true);
        setIsImageProcessing(!!selectedImage);

        // Add user message immediately with image preview if present
        const userMessage = {
            type: 'user',
            content: newQuestion || (selectedImage ? 'Uploaded an image' : ''),
            timestamp: new Date().toISOString(),
            hasImage: !!selectedImage,
            imagePreview: imagePreview
        };

        setMessages(prev => [...prev, userMessage]);

        // Add processing message
        const processingMessage = {
            type: 'assistant',
            content: selectedImage ? '📷 Processing image and extracting text...' : '🤔 Thinking...',
            timestamp: new Date().toISOString(),
            isProcessing: true
        };

        setMessages(prev => [...prev, processingMessage]);

        try {
            // Determine the endpoint
            const endpoint = 'chat_interaction';

            // Prepare headers
            const headers = {};
            if (authToken) {
                headers['Authorization'] = `Token ${authToken}`;
            }

            let requestBody;
            let requestHeaders = { ...headers };

            // Check if we have an image to upload
            if (selectedImage) {
                // Use FormData for image upload
                const formData = new FormData();
                formData.append('question', newQuestion || '');
                formData.append('image', selectedImage);
                formData.append('use_rag', useRAG.toString());
                
                // Include selected documents if any
                if (selectedDocuments.length > 0) {
                    selectedDocuments.forEach(docId => {
                        formData.append('document_ids', docId);
                    });
                }

                requestBody = formData;
                // Don't set Content-Type for FormData, let browser set it with boundary
            } else {
                // Use JSON for text-only requests
                requestHeaders['Content-Type'] = 'application/json';
                
                const requestData = {
                    question: newQuestion,
                    use_rag: useRAG
                };

                // Include selected documents if any
                if (selectedDocuments.length > 0) {
                    requestData.document_ids = selectedDocuments;
                }

                requestBody = JSON.stringify(requestData);
            }

            console.log('Sending request:', {
                endpoint,
                hasImage: !!selectedImage,
                selectedDocuments,
                documentsCount: uploadedDocuments.length,
                question: newQuestion ? newQuestion.substring(0, 50) + '...' : 'Image only',
                useFormData: !!selectedImage,
                formDataEntries: selectedImage ? Array.from(requestBody.entries()).map(([key, value]) => [key, typeof value === 'object' ? `File: ${value.name}` : value]) : 'N/A'
            });
            
            const response = await fetch(`http://127.0.0.1:8000/api/${endpoint}/`, {
                method: 'POST',
                headers: requestHeaders,
                body: requestBody,
            });

            const data = await response.json();

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
                
                // Handle OCR-specific errors more gracefully
                if (data.error && selectedImage) {
                    setMessages(prev => {
                        const filteredMessages = prev.filter(msg => !msg.isProcessing);
                        return [...filteredMessages, {
                            type: 'error',
                            content: `📷 Image Processing Issue:\n${data.error}\n\n${data.suggestion || 'Try uploading a clearer image with printed text.'}`,
                            timestamp: new Date().toISOString(),
                            ocrMetadata: data.ocr_metadata,
                            processingErrors: data.processing_errors
                        }];
                    });
                    return;
                }
                
                throw new Error(`Network response was not ok: ${response.status}`);
            }
            
            console.log('Received response:', {
                source: data.source,
                documentsUsed: data.documents_used,
                hasAnswer: !!data.answer,
                hasExtractedText: !!data.extracted_text,
                ocrConfidence: data.ocr_metadata?.overall_confidence
            });
            
            // Create the bot response message
            let botMessage = {
                type: data.source === 'document_rag' || data.source === 'documents' ? 'document' : 'assistant',
                content: data.answer,
                timestamp: new Date().toISOString(),
                source: data.source,
                documentsUsed: data.documents_used || [],
                processingInfo: data.processing_info,
                chatId: data.chat_id,
                extractedText: data.extracted_text,
                ocrMetadata: data.ocr_metadata
            };

            // If we have extracted text from image, show it in a special format
            if (data.extracted_text && selectedImage) {
                const confidence = data.ocr_metadata?.overall_confidence || 0;
                const quality = data.ocr_metadata?.text_quality || 'unknown';
                
                botMessage.content = `📷 **Image Text Extracted** (Confidence: ${confidence.toFixed(1)}%, Quality: ${quality})\n\n**Extracted Text:**\n"${data.extracted_text}"\n\n**AI Response:**\n${data.answer}`;
            } else if (selectedImage && data.ocr_feedback) {
                // Show OCR feedback when no text was extracted but processing continued
                botMessage.content = `📷 **Image Processing Note:**\n${data.ocr_feedback}\n\n**AI Response to your question:**\n${data.answer}`;
                botMessage.type = 'assistant'; // Use regular assistant styling
            }
            
            // Remove processing message and add bot response
            setMessages(prev => {
                const filteredMessages = prev.filter(msg => !msg.isProcessing);
                return [...filteredMessages, botMessage];
            });

        } catch (error) {
            console.error('Error:', error);
            
            // Remove processing message and add error message
            setMessages(prev => {
                const filteredMessages = prev.filter(msg => !msg.isProcessing);
                return [...filteredMessages, {
                    type: 'error',
                    content: `Error: ${error.message}. Please check your connection and try again.`,
                    timestamp: new Date().toISOString()
                }];
            });
        } finally {
            setIsLoading(false);
            setIsImageProcessing(false);
            setNewQuestion('');
            
            // Clear image after sending
            if (selectedImage) {
                handleRemoveImage();
            }
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

    // Image upload handling functions
    const handleImageSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            // Validate file type
            const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp'];
            if (!validTypes.includes(file.type)) {
                alert('Please select a valid image file (JPEG, PNG, GIF, or BMP)');
                return;
            }

            // Validate file size (max 10MB)
            if (file.size > 10 * 1024 * 1024) {
                alert('Image file size must be less than 10MB');
                return;
            }

            setSelectedImage(file);
            
            // Create preview
            const reader = new FileReader();
            reader.onload = (e) => {
                setImagePreview(e.target.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleRemoveImage = () => {
        setSelectedImage(null);
        setImagePreview(null);
        if (imageInputRef.current) {
            imageInputRef.current.value = '';
        }
    };

    const handleImageClick = () => {
        if (imageInputRef.current) {
            imageInputRef.current.click();
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
                    {/* Show image preview for user messages with images */}
                    {message.hasImage && message.imagePreview && (
                        <Box sx={{ mb: 1 }}>
                            <img 
                                src={message.imagePreview} 
                                alt="Uploaded" 
                                style={{ 
                                    maxWidth: '200px', 
                                    maxHeight: '200px', 
                                    borderRadius: '8px',
                                    objectFit: 'contain'
                                }} 
                            />
                        </Box>
                    )}
                    
                    <Typography>{message.content}</Typography>
                    
                    {/* Show extracted text info for OCR responses */}
                    {message.extractedText && (
                        <Box sx={{ mt: 1, p: 1, backgroundColor: 'rgba(0,0,0,0.05)', borderRadius: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                                📷 Extracted from image:
                            </Typography>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace', mt: 0.5 }}>
                                "{message.extractedText}"
                            </Typography>
                            {message.ocrMetadata && (
                                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                                    Confidence: {message.ocrMetadata.overall_confidence?.toFixed(1)}%, 
                                    Quality: {message.ocrMetadata.text_quality}
                                </Typography>
                            )}
                        </Box>
                    )}
                    
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
            {/* Enhanced Top Navigation Bar */}
            <Box 
                sx={{ 
                    height: '80px',
                    background: 'linear-gradient(135deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0.1) 100%)',
                    backdropFilter: 'blur(40px)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    px: 4,
                    boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
                    border: '1px solid rgba(255,255,255,0.4)',
                    borderBottom: '1px solid rgba(255,255,255,0.3)',
                    zIndex: 1100,
                    position: 'relative',
                    '&::before': {
                        content: '""',
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0.1) 100%)',
                        zIndex: -1,
                        animation: 'shimmer 3s ease-in-out infinite',
                    },
                    '@keyframes shimmer': {
                        '0%, 100%': { opacity: 0.5 },
                        '50%': { opacity: 1 }
                    }
                }}
            >
                {/* Left side - Brand and mode indicator */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Box 
                            sx={{ 
                                background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%)',
                                borderRadius: '50%',
                                p: 1.5,
                                backdropFilter: 'blur(20px)',
                                border: '2px solid rgba(255,255,255,0.5)',
                                boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
                                animation: 'pulse 2s ease-in-out infinite',
                                '@keyframes pulse': {
                                    '0%, 100%': { transform: 'scale(1)' },
                                    '50%': { transform: 'scale(1.05)' }
                                }
                            }}
                        >
                            <AutoAwesomeIcon sx={{ fontSize: 28, color: '#667eea', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))' }} />
                        </Box>
                        <Box>
                            <Typography 
                                variant="h4" 
                                sx={{ 
                                    color: 'white',
                                    fontWeight: 800,
                                    textShadow: '0 4px 12px rgba(0,0,0,0.5)',
                                    letterSpacing: '1px',
                                    background: 'linear-gradient(135deg, #ffffff 0%, #f0f8ff 100%)',
                                    backgroundClip: 'text',
                                    WebkitBackgroundClip: 'text',
                                    WebkitTextFillColor: 'transparent',
                                    lineHeight: 1
                                }}
                            >
                                Enhanced AI Chatbot
                            </Typography>
                            <Typography 
                                variant="caption" 
                                sx={{ 
                                    color: 'rgba(255, 255, 255, 0.8)',
                                    fontSize: '0.75rem',
                                    fontWeight: 500,
                                    textShadow: '0 2px 4px rgba(0,0,0,0.3)'
                                }}
                            >
                                Powered by RAG Technology
                            </Typography>
                        </Box>
                    </Box>
                    
                    <Chip 
                        label={useRAG ? '🚀 RAG Mode Active' : '⚡ Standard Mode'}
                        size="medium"
                        sx={{ 
                            backgroundColor: useRAG ? 'rgba(76, 205, 50, 0.9)' : 'rgba(255, 193, 7, 0.9)',
                            color: 'white',
                            fontWeight: 700,
                            fontSize: '0.8rem',
                            backdropFilter: 'blur(20px)',
                            border: '2px solid rgba(255,255,255,0.4)',
                            boxShadow: '0 6px 20px rgba(0,0,0,0.2)',
                            px: 1,
                            animation: useRAG ? 'glow 2s ease-in-out infinite' : 'none',
                            '@keyframes glow': {
                                '0%, 100%': { boxShadow: '0 6px 20px rgba(76, 205, 50, 0.3)' },
                                '50%': { boxShadow: '0 6px 20px rgba(76, 205, 50, 0.6)' }
                            },
                            '&:hover': {
                                transform: 'scale(1.05)',
                                boxShadow: '0 8px 24px rgba(0,0,0,0.3)'
                            },
                            transition: 'all 0.3s ease'
                        }}
                    />
                </Box>
                
                {/* Right side - Enhanced action buttons */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    {/* RAG Mode Toggle with enhanced styling */}
                    <Box 
                        sx={{ 
                            background: 'rgba(255, 255, 255, 0.15)',
                            backdropFilter: 'blur(20px)',
                            borderRadius: '25px',
                            p: 1,
                            border: '1px solid rgba(255,255,255,0.3)',
                            boxShadow: '0 4px 16px rgba(0,0,0,0.1)'
                        }}
                    >
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={useRAG}
                                    onChange={(e) => setUseRAG(e.target.checked)}
                                    sx={{
                                        '& .MuiSwitch-thumb': {
                                            backgroundColor: 'white',
                                            boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
                                            width: 24,
                                            height: 24
                                        },
                                        '& .MuiSwitch-track': {
                                            backgroundColor: 'rgba(255,255,255,0.4)',
                                            border: '2px solid rgba(255,255,255,0.6)',
                                            borderRadius: '12px'
                                        },
                                        '& .Mui-checked + .MuiSwitch-track': {
                                            backgroundColor: 'rgba(76, 205, 50, 0.8)',
                                        }
                                    }}
                                />
                            }
                            label={
                                <Typography sx={{ 
                                    color: 'white', 
                                    fontWeight: 600, 
                                    fontSize: '0.9rem',
                                    textShadow: '0 2px 4px rgba(0,0,0,0.3)'
                                }}>
                                    RAG Mode
                                </Typography>
                            }
                        />
                    </Box>

                    {/* Enhanced Documents Button */}
                    <Button
                        startIcon={<HistoryIcon />}
                        onClick={() => setShowDocuments(!showDocuments)}
                        variant="outlined"
                        size="medium"
                        sx={{
                            color: 'white',
                            borderColor: 'rgba(255,255,255,0.6)',
                            backgroundColor: 'rgba(255,255,255,0.15)',
                            backdropFilter: 'blur(20px)',
                            borderRadius: '20px',
                            px: 3,
                            py: 1,
                            fontWeight: 600,
                            fontSize: '0.85rem',
                            textTransform: 'none',
                            border: '2px solid rgba(255,255,255,0.4)',
                            boxShadow: '0 6px 20px rgba(0,0,0,0.15)',
                            '&:hover': {
                                backgroundColor: 'rgba(255,255,255,0.25)',
                                borderColor: 'rgba(255,255,255,0.8)',
                                transform: 'translateY(-2px)',
                                boxShadow: '0 8px 24px rgba(0,0,0,0.2)'
                            },
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                        }}
                    >
                        📚 Documents ({uploadedDocuments.length})
                    </Button>

                    {/* Enhanced Clear Memory Button */}
                    <Button
                        startIcon={<MemoryIcon />}
                        onClick={clearMemory}
                        variant="outlined"
                        size="medium"
                        sx={{
                            color: 'white',
                            borderColor: 'rgba(255,152,0,0.8)',
                            backgroundColor: 'rgba(255,152,0,0.15)',
                            backdropFilter: 'blur(20px)',
                            borderRadius: '20px',
                            px: 3,
                            py: 1,
                            fontWeight: 600,
                            fontSize: '0.85rem',
                            textTransform: 'none',
                            border: '2px solid rgba(255,152,0,0.6)',
                            boxShadow: '0 6px 20px rgba(255,152,0,0.2)',
                            '&:hover': {
                                backgroundColor: 'rgba(255,152,0,0.25)',
                                borderColor: 'rgba(255,152,0,1)',
                                transform: 'translateY(-2px)',
                                boxShadow: '0 8px 24px rgba(255,152,0,0.3)'
                            },
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                        }}
                        title="Clear conversation memory and delete all uploaded files"
                    >
                        🧹 Clear Memory
                    </Button>

                    {/* Enhanced Clear Chat Button */}
                    <Button
                        startIcon={<ClearIcon />}
                        onClick={() => {
                            setMessages([]);
                            localStorage.removeItem('chatbot_messages');
                        }}
                        variant="outlined"
                        size="medium"
                        sx={{
                            color: 'white',
                            borderColor: 'rgba(244,67,54,0.8)',
                            backgroundColor: 'rgba(244,67,54,0.15)',
                            backdropFilter: 'blur(20px)',
                            borderRadius: '20px',
                            px: 3,
                            py: 1,
                            fontWeight: 600,
                            fontSize: '0.85rem',
                            textTransform: 'none',
                            border: '2px solid rgba(244,67,54,0.6)',
                            boxShadow: '0 6px 20px rgba(244,67,54,0.2)',
                            '&:hover': {
                                backgroundColor: 'rgba(244,67,54,0.25)',
                                borderColor: 'rgba(244,67,54,1)',
                                transform: 'translateY(-2px)',
                                boxShadow: '0 8px 24px rgba(244,67,54,0.3)'
                            },
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                        }}
                    >
                        🗑️ Clear Chat
                    </Button>
                </Box>
            </Box>

            {/* Document list */}
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
                <div ref={messagesEndRef} />
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
                    
                    <input
                        type="file"
                        ref={imageInputRef}
                        onChange={handleImageSelect}
                        style={{ display: 'none' }}
                        accept="image/*"
                    />
                    
                    {/* Image preview area */}
                    {imagePreview && (
                        <Box sx={{ 
                            mb: 2, 
                            p: 2, 
                            backgroundColor: 'rgba(255, 255, 255, 0.9)',
                            borderRadius: 2,
                            display: 'flex',
                            alignItems: 'center',
                            gap: 2
                        }}>
                            <img 
                                src={imagePreview} 
                                alt="Preview" 
                                style={{ 
                                    maxWidth: '100px', 
                                    maxHeight: '100px', 
                                    borderRadius: '8px',
                                    objectFit: 'contain'
                                }} 
                            />
                            <Box sx={{ flex: 1 }}>
                                <Typography variant="body2" color="text.secondary">
                                    📷 Image ready for upload
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    {selectedImage?.name} ({(selectedImage?.size / 1024).toFixed(1)} KB)
                                </Typography>
                            </Box>
                            <IconButton 
                                onClick={handleRemoveImage}
                                size="small"
                                title="Remove image"
                                sx={{ color: 'error.main' }}
                            >
                                <ClearIcon />
                            </IconButton>
                        </Box>
                    )}
                    
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
                    
                    <IconButton
                        onClick={handleImageClick}
                        title="Upload image for OCR"
                        size="large"
                        disabled={isLoading || isUploading}
                        sx={{
                            backgroundColor: 'rgba(255, 255, 255, 0.9)',
                            backdropFilter: 'blur(10px)',
                            border: '1px solid rgba(255, 255, 255, 0.3)',
                            color: '#667eea',
                            ml: 1,
                            '&:hover': {
                                backgroundColor: 'rgba(255, 255, 255, 1)',
                                transform: 'scale(1.05)'
                            }
                        }}
                    >
                        <CameraAltIcon />
                    </IconButton>
                    
                    <TextField
                        fullWidth
                        multiline
                        maxRows={4}
                        value={newQuestion}
                        onChange={(e) => setNewQuestion(e.target.value)}
                        placeholder={selectedImage
                            ? "Add a question about your image, or send it as-is for text extraction..."
                            : selectedDocuments.length > 0 
                                ? `Ask about: ${selectedDocuments.map(id => {
                                    const doc = uploadedDocuments.find(d => d.id.toString() === id);
                                    return doc ? doc.title : 'document';
                                }).join(', ')}...` 
                                : uploadedDocuments.length > 0 
                                    ? "Select documents above, upload an image (📷), or ask general questions..."
                                    : "Ask me anything, upload a document (📎), or upload an image (📷) for text extraction..."
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
        </ChatContainer>
    );
};

export default ChatbotQuestions;
