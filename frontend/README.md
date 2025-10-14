# Exam System Frontend

A React TypeScript frontend for the Exam System, built with Vite, TailwindCSS, and shadcn/ui.

## Features

- **Student Dashboard**: Take interactive exams with real-time feedback
- **Teacher Dashboard**: Upload documents, create exams, monitor system health
- **Role-based Authentication**: Simple local authentication with role switching
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: Live exam progress and feedback

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **TailwindCSS** for styling
- **shadcn/ui** for UI components
- **React Router v6** for navigation
- **TanStack Query** for API state management
- **Radix UI** for accessible components

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on http://127.0.0.1:8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update `.env` with your API URL:
```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

4. Start development server:
```bash
npm run dev
```

5. Open http://localhost:5173 in your browser

## Project Structure

```
src/
├── components/
│   ├── ui/                 # shadcn/ui components
│   └── ProtectedRoute.tsx  # Route protection
├── hooks/
│   └── use-toast.ts       # Toast notifications
├── lib/
│   ├── api.ts             # API client and types
│   ├── auth.tsx           # Authentication context
│   └── utils.ts           # Utility functions
├── routes/
│   ├── SignIn.tsx         # Login page
│   ├── Student/
│   │   ├── StudentDashboard.tsx
│   │   ├── ExamRunner.tsx
│   │   └── QuestionCard.tsx
│   └── Teacher/
│       ├── TeacherDashboard.tsx
│       ├── UploadDocument.tsx
│       ├── CreateExam.tsx
│       ├── HealthPanel.tsx
│       └── ExamResults.tsx
├── App.tsx                # Main app component
├── main.tsx              # Entry point
└── index.css             # Global styles
```

## API Integration

The frontend integrates with the Django backend API:

- **Health Check**: `GET /api/health/`
- **Document Upload**: `POST /api/documents/upload/`
- **Create Exam**: `POST /api/exams/create/`
- **Start Exam**: `POST /api/exams/{id}/start/`
- **Get Questions**: `GET /api/exams/{id}/questions/`
- **Submit Answers**: `POST /api/exams/{id}/submit/`
- **Finish Exam**: `POST /api/exams/{id}/finish/`

## Features

### Student Features
- Sign in as student
- Enter exam ID to start exam
- Answer questions (MCQ and open-ended)
- Real-time feedback and hints
- Progress tracking
- Timer countdown
- Session persistence

### Teacher Features
- Sign in as teacher
- Upload PDF/text documents
- Create exams from documents
- Generate shareable exam links
- Monitor API health
- View exam results (placeholder)

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Environment Variables

- `VITE_API_BASE_URL` - Backend API base URL (default: http://127.0.0.1:8000)

## Deployment

1. Build the project:
```bash
npm run build
```

2. Serve the `dist` folder with any static file server

3. Update `VITE_API_BASE_URL` to point to your production API

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the Exam System and follows the same license terms.
