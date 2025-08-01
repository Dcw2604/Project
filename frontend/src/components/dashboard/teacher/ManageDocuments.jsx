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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  IconButton,
  LinearProgress,
  Paper,
  Divider,
  styled,
  Tabs,
  Tab,
  Avatar,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondary,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  CloudUpload,
  Description,
  PictureAsPdf,
  Image,
  VideoFile,
  AudioFile,
  Code,
  Download,
  Delete,
  Edit,
  Share,
  Visibility,
  Add,
  Folder,
  Search,
  FilterList,
  ExpandMore,
  School,
  Assessment,
  Assignment,
  Quiz,
  MenuBook,
  InsertDriveFile
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

const UploadZone = styled(Paper)(({ theme }) => ({
  padding: '40px',
  textAlign: 'center',
  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05))',
  backdropFilter: 'blur(20px)',
  border: '2px dashed rgba(255, 255, 255, 0.3)',
  borderRadius: '20px',
  color: 'white',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
  '&:hover': {
    borderColor: '#10B981',
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
  }
}));

const DocumentCard = styled(GlassCard)(({ theme }) => ({
  cursor: 'pointer',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: '0 16px 48px rgba(0, 0, 0, 0.2)',
  }
}));

const ManageDocuments = () => {
  const [documents, setDocuments] = useState([
    {
      id: 1,
      name: 'Algebra Fundamentals.pdf',
      type: 'pdf',
      subject: 'Mathematics',
      category: 'textbook',
      size: '2.4 MB',
      uploadDate: '2025-07-15',
      downloads: 24,
      shared: true,
      description: 'Complete guide to algebra basics and advanced concepts'
    },
    {
      id: 2,
      name: 'Physics Lab Manual.pdf',
      type: 'pdf',
      subject: 'Physics',
      category: 'manual',
      size: '5.1 MB',
      uploadDate: '2025-07-10',
      downloads: 18,
      shared: true,
      description: 'Laboratory experiments and procedures for physics students'
    },
    {
      id: 3,
      name: 'Chemistry Reactions.pptx',
      type: 'presentation',
      subject: 'Chemistry',
      category: 'lesson',
      size: '8.2 MB',
      uploadDate: '2025-07-20',
      downloads: 31,
      shared: false,
      description: 'Interactive presentation on chemical reactions and equations'
    },
    {
      id: 4,
      name: 'Math Quiz Questions.docx',
      type: 'document',
      subject: 'Mathematics',
      category: 'assessment',
      size: '450 KB',
      uploadDate: '2025-07-25',
      downloads: 12,
      shared: true,
      description: 'Collection of quiz questions for different math topics'
    },
    {
      id: 5,
      name: 'Biology Diagrams.zip',
      type: 'archive',
      subject: 'Biology',
      category: 'resource',
      size: '15.3 MB',
      uploadDate: '2025-07-28',
      downloads: 8,
      shared: false,
      description: 'High-resolution diagrams for biology lessons'
    }
  ]);

  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSubject, setFilterSubject] = useState('all');
  const [filterCategory, setFilterCategory] = useState('all');
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English'];
  const categories = ['textbook', 'manual', 'lesson', 'assessment', 'resource'];

  const getFileIcon = (type) => {
    switch (type) {
      case 'pdf': return <PictureAsPdf sx={{ fontSize: '2rem', color: '#EF4444' }} />;
      case 'document': return <Description sx={{ fontSize: '2rem', color: '#3B82F6' }} />;
      case 'presentation': return <Assignment sx={{ fontSize: '2rem', color: '#F59E0B' }} />;
      case 'image': return <Image sx={{ fontSize: '2rem', color: '#10B981' }} />;
      case 'video': return <VideoFile sx={{ fontSize: '2rem', color: '#8B5CF6' }} />;
      case 'audio': return <AudioFile sx={{ fontSize: '2rem', color: '#F97316' }} />;
      case 'archive': return <Folder sx={{ fontSize: '2rem', color: '#6B7280' }} />;
      default: return <InsertDriveFile sx={{ fontSize: '2rem', color: '#6B7280' }} />;
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'textbook': return <MenuBook sx={{ color: '#3B82F6' }} />;
      case 'manual': return <Description sx={{ color: '#10B981' }} />;
      case 'lesson': return <School sx={{ color: '#F59E0B' }} />;
      case 'assessment': return <Quiz sx={{ color: '#EF4444' }} />;
      case 'resource': return <Assignment sx={{ color: '#8B5CF6' }} />;
      default: return <InsertDriveFile sx={{ color: '#6B7280' }} />;
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'textbook': return '#3B82F6';
      case 'manual': return '#10B981';
      case 'lesson': return '#F59E0B';
      case 'assessment': return '#EF4444';
      case 'resource': return '#8B5CF6';
      default: return '#6B7280';
    }
  };

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSubject = filterSubject === 'all' || doc.subject === filterSubject;
    const matchesCategory = filterCategory === 'all' || doc.category === filterCategory;
    
    return matchesSearch && matchesSubject && matchesCategory;
  });

  const handleFileUpload = (event) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      setIsUploading(true);
      setUploadProgress(0);
      
      // Simulate upload progress
      const interval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            setIsUploading(false);
            // Add uploaded file to documents
            const newDoc = {
              id: documents.length + 1,
              name: files[0].name,
              type: files[0].type.includes('pdf') ? 'pdf' : 'document',
              subject: 'Mathematics', // Default subject
              category: 'resource',
              size: `${(files[0].size / (1024 * 1024)).toFixed(1)} MB`,
              uploadDate: new Date().toISOString().split('T')[0],
              downloads: 0,
              shared: false,
              description: 'Recently uploaded document'
            };
            setDocuments([newDoc, ...documents]);
            return 100;
          }
          return prev + 10;
        });
      }, 200);
    }
  };

  const handleDocumentClick = (document) => {
    setSelectedDocument(document);
    setDialogOpen(true);
  };

  const handleDeleteDocument = (docId) => {
    setDocuments(documents.filter(doc => doc.id !== docId));
  };

  const renderUploadSection = () => (
    <GlassCard>
      <CardContent sx={{ p: 4 }}>
        <Typography variant="h6" fontWeight={700} mb={3}>
          Upload Documents
        </Typography>
        
        <input
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.zip,.rar"
          onChange={handleFileUpload}
          style={{ display: 'none' }}
          id="file-upload"
        />
        
        <label htmlFor="file-upload">
          <UploadZone component="div">
            <CloudUpload sx={{ fontSize: '3rem', color: '#10B981', mb: 2 }} />
            <Typography variant="h6" fontWeight={600} mb={1}>
              Drop files here or click to browse
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Supported formats: PDF, DOC, PPT, XLS, ZIP (Max 50MB)
            </Typography>
          </UploadZone>
        </label>
        
        {isUploading && (
          <Box mt={3}>
            <Typography variant="body2" mb={1}>
              Uploading... {uploadProgress}%
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={uploadProgress}
              sx={{
                height: 8,
                borderRadius: 4,
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 4,
                  bgcolor: '#10B981'
                }
              }}
            />
          </Box>
        )}
      </CardContent>
    </GlassCard>
  );

  const renderDocumentGrid = () => (
    <Grid container spacing={3}>
      {filteredDocuments.map((document) => (
        <Grid item xs={12} sm={6} md={4} key={document.id}>
          <DocumentCard onClick={() => handleDocumentClick(document)}>
            <CardContent sx={{ p: 3 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="flex-start" mb={2}>
                {getFileIcon(document.type)}
                <IconButton 
                  size="small" 
                  sx={{ color: 'white' }}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteDocument(document.id);
                  }}
                >
                  <Delete />
                </IconButton>
              </Stack>
              
              <Typography variant="h6" fontWeight={700} mb={1} sx={{ 
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}>
                {document.name}
              </Typography>
              
              <Typography variant="body2" sx={{ opacity: 0.8, mb: 2, height: '3em', overflow: 'hidden' }}>
                {document.description}
              </Typography>
              
              <Stack direction="row" spacing={1} mb={2}>
                <Chip 
                  label={document.subject}
                  size="small"
                  sx={{ bgcolor: '#3B82F6', color: 'white' }}
                />
                <Chip 
                  icon={getCategoryIcon(document.category)}
                  label={document.category}
                  size="small"
                  sx={{ bgcolor: getCategoryColor(document.category), color: 'white' }}
                />
              </Stack>
              
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Typography variant="caption" sx={{ opacity: 0.8 }}>
                  {document.size} • {document.downloads} downloads
                </Typography>
                {document.shared && (
                  <Chip 
                    label="Shared"
                    size="small"
                    sx={{ bgcolor: '#10B981', color: 'white' }}
                  />
                )}
              </Stack>
            </CardContent>
          </DocumentCard>
        </Grid>
      ))}
    </Grid>
  );

  const renderDocumentList = () => (
    <GlassCard>
      <CardContent sx={{ p: 0 }}>
        <List>
          {filteredDocuments.map((document, index) => (
            <React.Fragment key={document.id}>
              <ListItem 
                sx={{ 
                  cursor: 'pointer',
                  '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)' }
                }}
                onClick={() => handleDocumentClick(document)}
              >
                <ListItemIcon>
                  {getFileIcon(document.type)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="body1" fontWeight={600} color="white">
                      {document.name}
                    </Typography>
                  }
                  secondary={
                    <Stack direction="row" spacing={2} alignItems="center" mt={1}>
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                        {document.subject} • {document.size} • {document.uploadDate}
                      </Typography>
                      <Chip 
                        label={document.category}
                        size="small"
                        sx={{ bgcolor: getCategoryColor(document.category), color: 'white' }}
                      />
                    </Stack>
                  }
                />
                <Stack direction="row" spacing={1}>
                  <IconButton size="small" sx={{ color: 'white' }}>
                    <Download />
                  </IconButton>
                  <IconButton size="small" sx={{ color: 'white' }}>
                    <Share />
                  </IconButton>
                  <IconButton 
                    size="small" 
                    sx={{ color: '#EF4444' }}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteDocument(document.id);
                    }}
                  >
                    <Delete />
                  </IconButton>
                </Stack>
              </ListItem>
              {index < filteredDocuments.length - 1 && (
                <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)' }} />
              )}
            </React.Fragment>
          ))}
        </List>
      </CardContent>
    </GlassCard>
  );

  const renderStatistics = () => (
    <Grid container spacing={3} mb={4}>
      <Grid item xs={12} sm={6} md={3}>
        <GlassCard>
          <CardContent sx={{ p: 3, textAlign: 'center' }}>
            <Description sx={{ fontSize: '2.5rem', color: '#3B82F6', mb: 1 }} />
            <Typography variant="h4" fontWeight={800}>
              {documents.length}
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Total Documents
            </Typography>
          </CardContent>
        </GlassCard>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <GlassCard>
          <CardContent sx={{ p: 3, textAlign: 'center' }}>
            <Share sx={{ fontSize: '2.5rem', color: '#10B981', mb: 1 }} />
            <Typography variant="h4" fontWeight={800}>
              {documents.filter(doc => doc.shared).length}
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Shared Documents
            </Typography>
          </CardContent>
        </GlassCard>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <GlassCard>
          <CardContent sx={{ p: 3, textAlign: 'center' }}>
            <Download sx={{ fontSize: '2.5rem', color: '#F59E0B', mb: 1 }} />
            <Typography variant="h4" fontWeight={800}>
              {documents.reduce((total, doc) => total + doc.downloads, 0)}
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Total Downloads
            </Typography>
          </CardContent>
        </GlassCard>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <GlassCard>
          <CardContent sx={{ p: 3, textAlign: 'center' }}>
            <CloudUpload sx={{ fontSize: '2.5rem', color: '#8B5CF6', mb: 1 }} />
            <Typography variant="h4" fontWeight={800}>
              {(documents.reduce((total, doc) => total + parseFloat(doc.size), 0)).toFixed(1)}
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Total Size (MB)
            </Typography>
          </CardContent>
        </GlassCard>
      </Grid>
    </Grid>
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" fontWeight={800} color="white" mb={1}>
            Document Management
          </Typography>
          <Typography variant="h6" sx={{ opacity: 0.9, color: 'white' }}>
            Upload and manage educational resources
          </Typography>
        </Box>
        <ActionButton startIcon={<Add />}>
          Quick Upload
        </ActionButton>
      </Stack>

      {/* Statistics */}
      {renderStatistics()}

      {/* Search and Filters */}
      <GlassCard>
        <CardContent sx={{ p: 3 }}>
          <Stack direction="row" spacing={2} alignItems="center">
            <TextField
              placeholder="Search documents..."
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
              label="Subject"
              value={filterSubject}
              onChange={(e) => setFilterSubject(e.target.value)}
              sx={{
                minWidth: 120,
                '& .MuiOutlinedInput-root': {
                  color: 'white',
                  '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                },
                '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.7)' },
                '& .MuiSelect-icon': { color: 'white' }
              }}
            >
              <MenuItem value="all">All Subjects</MenuItem>
              {subjects.map((subject) => (
                <MenuItem key={subject} value={subject}>{subject}</MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Category"
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              sx={{
                minWidth: 120,
                '& .MuiOutlinedInput-root': {
                  color: 'white',
                  '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                },
                '& .MuiInputLabel-root': { color: 'rgba(255, 255, 255, 0.7)' },
                '& .MuiSelect-icon': { color: 'white' }
              }}
            >
              <MenuItem value="all">All Categories</MenuItem>
              {categories.map((category) => (
                <MenuItem key={category} value={category}>{category}</MenuItem>
              ))}
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
          <Tab icon={<CloudUpload />} label="Upload" />
          <Tab icon={<Assessment />} label="Grid View" />
          <Tab icon={<Description />} label="List View" />
        </Tabs>
      </Box>

      {/* Content Based on Active Tab */}
      {activeTab === 0 && renderUploadSection()}
      {activeTab === 1 && renderDocumentGrid()}
      {activeTab === 2 && renderDocumentList()}

      {/* Document Detail Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={() => setDialogOpen(false)}
        maxWidth="sm"
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
        {selectedDocument && (
          <>
            <DialogTitle>
              <Stack direction="row" alignItems="center" spacing={2}>
                {getFileIcon(selectedDocument.type)}
                <Box>
                  <Typography variant="h6" fontWeight={700}>
                    {selectedDocument.name}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    {selectedDocument.subject} • {selectedDocument.size}
                  </Typography>
                </Box>
              </Stack>
            </DialogTitle>
            
            <DialogContent>
              <Stack spacing={2}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>Description</Typography>
                  <Typography variant="body1">{selectedDocument.description}</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>Category</Typography>
                  <Chip 
                    icon={getCategoryIcon(selectedDocument.category)}
                    label={selectedDocument.category}
                    sx={{ bgcolor: getCategoryColor(selectedDocument.category), color: 'white' }}
                  />
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>Upload Date</Typography>
                  <Typography variant="body1">{selectedDocument.uploadDate}</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>Downloads</Typography>
                  <Typography variant="body1">{selectedDocument.downloads}</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>Sharing Status</Typography>
                  <Chip 
                    label={selectedDocument.shared ? 'Shared with students' : 'Private'}
                    sx={{ 
                      bgcolor: selectedDocument.shared ? '#10B981' : '#6B7280',
                      color: 'white'
                    }}
                  />
                </Box>
              </Stack>
            </DialogContent>
            
            <DialogActions sx={{ p: 3 }}>
              <ActionButton onClick={() => setDialogOpen(false)}>Close</ActionButton>
              <ActionButton startIcon={<Download />}>Download</ActionButton>
              <ActionButton startIcon={<Share />}>Share</ActionButton>
              <ActionButton startIcon={<Edit />}>Edit</ActionButton>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default ManageDocuments;
