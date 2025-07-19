import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../../hooks/useAuth';
import { 
    Box, 
    TextField, 
    IconButton, 
    Paper, 
    Typography, 
    CircularProgress,
    styled
} from '@mui/material';
import { 
    Send as SendIcon,
    AddPhotoAlternate as AddPhotoIcon 
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
    padding: theme.spacing(2),
    maxWidth: '70%',
    borderRadius: theme.spacing(2),
    ...(variant === 'user' && {
        backgroundColor: theme.palette.primary.main,
        color: theme.palette.primary.contrastText
    }),
    ...(variant === 'error' && {
        backgroundColor: theme.palette.error.light,
        color: theme.palette.error.contrastText
    })
}));

const ChatContainer = styled(Box)({
    height: '100%',
    display: 'flex',
    flexDirection: 'column'
});

const MessagesArea = styled(Box)(({ theme }) => ({
    flexGrow: 1,
    overflow: 'auto',
    padding: theme.spacing(3),
    backgroundColor: theme.palette.grey[100],
    display: 'flex',
    flexDirection: 'column'
}));

const InputArea = styled(Paper)(({ theme }) => ({
    padding: theme.spacing(2),
    borderTop: `1px solid ${theme.palette.divider}`,
    backgroundColor: theme.palette.background.paper,
    position: 'sticky',
    bottom: 0,
    zIndex: 1000
}));

const ChatbotQuestions = () => {
    const [messages, setMessages] = useState([]);
    const [newQuestion, setNewQuestion] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);
    const { authToken } = useAuth();

    // Auto-scroll to bottom when new messages arrive
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!newQuestion.trim() || isLoading) return;

        try {
            setIsLoading(true);
            const headers = {
                'Content-Type': 'application/json',
            };
            
            // Add auth token if available
            if (authToken) {
                headers['Authorization'] = `Bearer ${authToken}`;
            }

            const response = await fetch('http://127.0.0.1:8000/api/chat_interaction/', {
                method: 'POST',
                headers,
                body: JSON.stringify({ question: newQuestion }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            setMessages(prev => [...prev, {
                type: 'user',
                content: newQuestion
            }, {
                type: 'bot',
                content: data.answer
            }]);
            setNewQuestion('');
        } catch (error) {
            console.error('Error:', error);
            setMessages(prev => [...prev, {
                type: 'error',
                content: 'Sorry, there was an error processing your question.'
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileUpload = (e) => {
        const file = e.target.files?.[0];
        if (file) {
            // TODO: Implement file upload logic
            console.log('File selected:', file);
        }
    };

    return (
        <ChatContainer>
            {/* Chat messages area - Shows answers above the input */}
            <MessagesArea>
                {messages.length === 0 && (
                    <Box 
                        sx={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'center', 
                            height: '100%',
                            opacity: 0.6 
                        }}
                    >
                        <Typography variant="h6" color="text.secondary">
                            Start a conversation with the AI chatbot...
                        </Typography>
                    </Box>
                )}
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {messages.map((message, index) => (
                        <MessageContainer key={index} className={message.type === 'user' ? 'user' : ''}>
                            <MessageBubble 
                                variant={message.type} 
                                elevation={1}
                            >
                                <Typography>{message.content}</Typography>
                            </MessageBubble>
                        </MessageContainer>
                    ))}
                </Box>
                <div ref={messagesEndRef} />
            </MessagesArea>

            {/* Input area - Fixed at bottom */}
            <InputArea elevation={3}>
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
                        accept="image/*"
                    />
                    <IconButton
                        onClick={() => fileInputRef.current?.click()}
                        color="primary"
                        title="Add image"
                        size="large"
                    >
                        <AddPhotoIcon />
                    </IconButton>
                    
                    <TextField
                        fullWidth
                        multiline
                        maxRows={4}
                        value={newQuestion}
                        onChange={(e) => setNewQuestion(e.target.value)}
                        placeholder="Ask me anything..."
                        disabled={isLoading}
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
                        disabled={isLoading || !newQuestion.trim()}
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