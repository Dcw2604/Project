# Frontend Setup Instructions

## Quick Start

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file:**
   ```bash
   echo "VITE_API_BASE_URL=http://127.0.0.1:8000" > .env
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

5. **Open browser:**
   - Go to http://localhost:5173
   - Sign in as Student or Teacher
   - Test the exam system!

## Backend Requirements

Make sure your Django backend is running on http://127.0.0.1:8000 with these endpoints:

- `GET /api/health/` - Health check
- `POST /api/documents/upload/` - Document upload
- `POST /api/exams/create/` - Create exam
- `POST /api/exams/{id}/start/` - Start exam
- `GET /api/exams/{id}/questions/` - Get questions
- `POST /api/exams/{id}/submit/` - Submit answers
- `POST /api/exams/{id}/finish/` - Finish exam

## Testing the Flow

### Teacher Flow:
1. Sign in as Teacher
2. Upload a PDF document
3. Create an exam from the document
4. Copy the student exam link
5. Check API health

### Student Flow:
1. Sign in as Student
2. Enter exam ID or use the link from teacher
3. Start the exam
4. Answer questions (MCQ and open-ended)
5. Submit answers and get feedback
6. Complete the exam

## Troubleshooting

- **API Connection Issues**: Check that backend is running on correct port
- **CORS Errors**: Ensure Django CORS settings allow frontend origin
- **File Upload Issues**: Check file size limits and supported formats
- **Authentication Issues**: Check localStorage for auth data

## Production Build

```bash
npm run build
```

The built files will be in the `dist/` directory.
