import React, { useState } from 'react';
import { User, Book, Calendar, MessageCircle, FileText, Users, Clock, CheckCircle, X } from 'lucide-react';

// Main App Component
const App = () => {
  const [currentPage, setCurrentPage] = useState('landing');
  const [userType, setUserType] = useState(null);
  const [user, setUser] = useState(null);

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'landing':
        return <LandingPage setCurrentPage={setCurrentPage} setUserType={setUserType} />;
      case 'student-auth':
        return <StudentAuth setCurrentPage={setCurrentPage} setUser={setUser} />;
      case 'teacher-auth':
        return <TeacherAuth setCurrentPage={setCurrentPage} setUser={setUser} />;
      case 'student-dashboard':
        return <StudentDashboard user={user} setCurrentPage={setCurrentPage} />;
      case 'teacher-dashboard':
        return <TeacherDashboard user={user} setCurrentPage={setCurrentPage} />;
      default:
        return <LandingPage setCurrentPage={setCurrentPage} setUserType={setUserType} />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {renderCurrentPage()}
    </div>
  );
};

// Landing Page Component
const LandingPage = ({ setCurrentPage, setUserType }) => {
  const handleUserTypeSelection = (type) => {
    setUserType(type);
    setCurrentPage(type === 'student' ? 'student-auth' : 'teacher-auth');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">EduConnect</h1>
          <p className="text-xl text-gray-600">Connect, Learn, and Grow Together</p>
        </div>
        
        <div className="grid md:grid-cols-2 gap-8 max-w-2xl mx-auto">
          <div 
            onClick={() => handleUserTypeSelection('student')}
            className="bg-white rounded-xl shadow-lg p-8 cursor-pointer hover:shadow-xl transition-all duration-300 transform hover:scale-105"
          >
            <div className="text-center">
              <div className="bg-blue-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <User className="w-8 h-8 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Student Portal</h2>
              <p className="text-gray-600 mb-4">Access classes, take tests, and chat with AI tutors</p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• Schedule classes with teachers</li>
                <li>• Take level assessment tests</li>
                <li>• AI chatbot assistance</li>
                <li>• Track your progress</li>
              </ul>
            </div>
          </div>

          <div 
            onClick={() => handleUserTypeSelection('teacher')}
            className="bg-white rounded-xl shadow-lg p-8 cursor-pointer hover:shadow-xl transition-all duration-300 transform hover:scale-105"
          >
            <div className="text-center">
              <div className="bg-green-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Book className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Teacher Portal</h2>
              <p className="text-gray-600 mb-4">Manage students, schedule classes, and share knowledge</p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• Manage student requests</li>
                <li>• Set monthly availability</li>
                <li>• View student progress</li>
                <li>• Upload teaching materials</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Student Authentication Component
const StudentAuth = ({ setCurrentPage, setUser }) => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    phone: '',
    age: '',
    class: '',
    subject: '',
    points: 0
  });

  const handleSubmit = () => {
    setUser({ ...formData, type: 'student' });
    setCurrentPage('student-dashboard');
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="bg-white rounded-xl shadow-lg p-8 w-full max-w-md">
        <div className="text-center mb-6">
          <h2 className="text-3xl font-bold text-gray-800">
            {isSignUp ? 'Student Sign Up' : 'Student Sign In'}
          </h2>
        </div>

        <div className="space-y-4">
          {isSignUp && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <input
                  type="text"
                  name="firstName"
                  placeholder="First Name"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
                <input
                  type="text"
                  name="lastName"
                  placeholder="Last Name"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              <input
                type="tel"
                name="phone"
                placeholder="Phone Number"
                value={formData.phone}
                onChange={handleInputChange}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <div className="grid grid-cols-2 gap-4">
                <input
                  type="number"
                  name="age"
                  placeholder="Age"
                  value={formData.age}
                  onChange={handleInputChange}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
                <input
                  type="text"
                  name="class"
                  placeholder="Class"
                  value={formData.class}
                  onChange={handleInputChange}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              <select
                name="subject"
                value={formData.subject}
                onChange={handleInputChange}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="">Select Subject</option>
                <option value="math">Mathematics</option>
                <option value="science">Science</option>
                <option value="english">English</option>
                <option value="history">History</option>
                <option value="physics">Physics</option>
                <option value="chemistry">Chemistry</option>
              </select>
            </>
          )}
          
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleInputChange}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleInputChange}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />

          <button
            onClick={handleSubmit}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            {isSignUp ? 'Sign Up' : 'Sign In'}
          </button>
        </div>

        <div className="mt-6 text-center">
          <button
            onClick={() => setIsSignUp(!isSignUp)}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            {isSignUp ? 'Already have an account? Sign In' : 'Need an account? Sign Up'}
          </button>
        </div>

        <div className="mt-4 text-center">
          <button
            onClick={() => setCurrentPage('landing')}
            className="text-gray-500 hover:text-gray-700 text-sm"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

// Teacher Authentication Component
const TeacherAuth = ({ setCurrentPage, setUser }) => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    phone: '',
    subject: '',
    description: ''
  });

  const handleSubmit = () => {
    setUser({ ...formData, type: 'teacher' });
    setCurrentPage('teacher-dashboard');
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="bg-white rounded-xl shadow-lg p-8 w-full max-w-md">
        <div className="text-center mb-6">
          <h2 className="text-3xl font-bold text-gray-800">
            {isSignUp ? 'Teacher Sign Up' : 'Teacher Sign In'}
          </h2>
        </div>

        <div className="space-y-4">
          {isSignUp && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <input
                  type="text"
                  name="firstName"
                  placeholder="First Name"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  required
                />
                <input
                  type="text"
                  name="lastName"
                  placeholder="Last Name"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  required
                />
              </div>
              <input
                type="tel"
                name="phone"
                placeholder="Phone Number"
                value={formData.phone}
                onChange={handleInputChange}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
              <select
                name="subject"
                value={formData.subject}
                onChange={handleInputChange}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              >
                <option value="">Select Teaching Subject</option>
                <option value="math">Mathematics</option>
                <option value="science">Science</option>
                <option value="english">English</option>
                <option value="history">History</option>
                <option value="physics">Physics</option>
                <option value="chemistry">Chemistry</option>
              </select>
              <textarea
                name="description"
                placeholder="Short description for students"
                value={formData.description}
                onChange={handleInputChange}
                rows="3"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
            </>
          )}
          
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleInputChange}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleInputChange}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
          />

          <button
            onClick={handleSubmit}
            className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors font-semibold"
          >
            {isSignUp ? 'Sign Up' : 'Sign In'}
          </button>
        </div>

        <div className="mt-6 text-center">
          <button
            onClick={() => setIsSignUp(!isSignUp)}
            className="text-green-600 hover:text-green-800 text-sm"
          >
            {isSignUp ? 'Already have an account? Sign In' : 'Need an account? Sign Up'}
          </button>
        </div>

        <div className="mt-4 text-center">
          <button
            onClick={() => setCurrentPage('landing')}
            className="text-gray-500 hover:text-gray-700 text-sm"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

// Student Dashboard Component
const StudentDashboard = ({ user, setCurrentPage }) => {
  const [selectedOption, setSelectedOption] = useState('schedule');

  const renderDashboardContent = () => {
    switch (selectedOption) {
      case 'schedule':
        return <ScheduleClasses user={user} />;
      case 'chatbot':
        return <ChatbotQuestions user={user} />;
      case 'test':
        return <LevelTest user={user} />;
      case 'level':
        return <CheckLevel user={user} />;
      default:
        return <ScheduleClasses user={user} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-800">Student Dashboard</h1>
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">Welcome, {user?.firstName}!</span>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">Points:</span>
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm font-semibold">
                  {user?.points || 0}
                </span>
              </div>
              <button
                onClick={() => setCurrentPage('landing')}
                className="text-gray-500 hover:text-gray-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="md:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Navigation</h2>
              <nav className="space-y-2">
                <button
                  onClick={() => setSelectedOption('schedule')}
                  className={`w-full text-left px-4 py-2 rounded-lg flex items-center space-x-2 ${
                    selectedOption === 'schedule' ? 'bg-blue-100 text-blue-800' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Calendar className="w-5 h-5" />
                  <span>Schedule Classes</span>
                </button>
                <button
                  onClick={() => setSelectedOption('chatbot')}
                  className={`w-full text-left px-4 py-2 rounded-lg flex items-center space-x-2 ${
                    selectedOption === 'chatbot' ? 'bg-blue-100 text-blue-800' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <MessageCircle className="w-5 h-5" />
                  <span>AI Chatbot</span>
                </button>
                <button
                  onClick={() => setSelectedOption('test')}
                  className={`w-full text-left px-4 py-2 rounded-lg flex items-center space-x-2 ${
                    selectedOption === 'test' ? 'bg-blue-100 text-blue-800' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <FileText className="w-5 h-5" />
                  <span>Take Level Test</span>
                </button>
                <button
                  onClick={() => setSelectedOption('level')}
                  className={`w-full text-left px-4 py-2 rounded-lg flex items-center space-x-2 ${
                    selectedOption === 'level' ? 'bg-blue-100 text-blue-800' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <User className="w-5 h-5" />
                  <span>Check My Level</span>
                </button>
              </nav>
            </div>
          </div>

          <div className="md:col-span-3">
            <div className="bg-white rounded-lg shadow-md p-6">
              {renderDashboardContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Teacher Dashboard Component
const TeacherDashboard = ({ user, setCurrentPage }) => {
  const [selectedOption, setSelectedOption] = useState('students');

  const renderDashboardContent = () => {
    switch (selectedOption) {
      case 'students':
        return <ManageStudents user={user} />;
      case 'schedule':
        return <ManageSchedule user={user} />;
      case 'documents':
        return <ManageDocuments user={user} />;
      default:
        return <ManageStudents user={user} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-800">Teacher Dashboard</h1>
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">Welcome, {user?.firstName}!</span>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">Subject:</span>
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-sm font-semibold">
                  {user?.subject}
                </span>
              </div>
              <button
                onClick={() => setCurrentPage('landing')}
                className="text-gray-500 hover:text-gray-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="md:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Navigation</h2>
              <nav className="space-y-2">
                <button
                  onClick={() => setSelectedOption('students')}
                  className={`w-full text-left px-4 py-2 rounded-lg flex items-center space-x-2 ${
                    selectedOption === 'students' ? 'bg-green-100 text-green-800' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Users className="w-5 h-5" />
                  <span>Manage Students</span>
                </button>
                <button
                  onClick={() => setSelectedOption('schedule')}
                  className={`w-full text-left px-4 py-2 rounded-lg flex items-center space-x-2 ${
                    selectedOption === 'schedule' ? 'bg-green-100 text-green-800' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Clock className="w-5 h-5" />
                  <span>Set Availability</span>
                </button>
                <button
                  onClick={() => setSelectedOption('documents')}
                  className={`w-full text-left px-4 py-2 rounded-lg flex items-center space-x-2 ${
                    selectedOption === 'documents' ? 'bg-green-100 text-green-800' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <FileText className="w-5 h-5" />
                  <span>Upload Documents</span>
                </button>
              </nav>
            </div>
          </div>

          <div className="md:col-span-3">
            <div className="bg-white rounded-lg shadow-md p-6">
              {renderDashboardContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Student Dashboard Components
const ScheduleClasses = ({ user }) => {
  const [availableClasses, setAvailableClasses] = useState([
    { id: 1, teacher: 'Dr. Smith', subject: 'Mathematics', date: '2025-07-15', time: '10:00 AM', level: 'Intermediate' },
    { id: 2, teacher: 'Prof. Johnson', subject: 'Physics', date: '2025-07-16', time: '2:00 PM', level: 'Advanced' },
    { id: 3, teacher: 'Ms. Davis', subject: 'English', date: '2025-07-17', time: '11:00 AM', level: 'Beginner' },
  ]);

  const handleBookClass = (classId) => {
    alert(`Class booking request sent for class ${classId}`);
  };

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Available Classes</h2>
      <div className="space-y-4">
        {availableClasses.map((classItem) => (
          <div key={classItem.id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold text-gray-800">{classItem.subject}</h3>
                <p className="text-gray-600">Teacher: {classItem.teacher}</p>
                <p className="text-gray-600">Date: {classItem.date}</p>
                <p className="text-gray-600">Time: {classItem.time}</p>
                <span className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm mt-2">
                  {classItem.level}
                </span>
              </div>
              <button
                onClick={() => handleBookClass(classItem.id)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Book Class
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const ChatbotQuestions = ({ user }) => {
  const [messages, setMessages] = useState([
    { id: 1, type: 'bot', content: 'Hello! I\'m here to help you with your studies. What would you like to know?' }
  ]);
  const [inputMessage, setInputMessage] = useState('');

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      setMessages([...messages, 
        { id: Date.now(), type: 'user', content: inputMessage },
        { id: Date.now() + 1, type: 'bot', content: 'Thanks for your question! I\'m processing your request...' }
      ]);
      setInputMessage('');
    }
  };

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-4">AI Learning Assistant</h2>
      <div className="border border-gray-200 rounded-lg h-96 flex flex-col">
        <div className="flex-1 p-4 overflow-y-auto space-y-3">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs px-4 py-2 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-800'
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}
        </div>
        <div className="border-t border-gray-200 p-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Ask me anything about your studies..."
              className="flex-1 p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={handleSendMessage}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const LevelTest = ({ user }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);

  const questions = [
    {
      question: "What is 2 + 2?",
      options: ["3", "4", "5", "6"],
      correct: "4"
    },
    {
      question: "Which planet is closest to the Sun?",
      options: ["Venus", "Mercury", "Mars", "Earth"],
      correct: "Mercury"
    },
    {
      question: "What is the capital of France?",
      options: ["London", "Berlin", "Paris", "Rome"],
      correct: "Paris"
    }
  ];

  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer('');
    } else {
      setShowResult(true);
    }
  };

  if (showResult) {
    return (
      <div className="text-center">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Test Complete!</h2>
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg">
          <p className="font-semibold">Your level: Intermediate</p>
          <p className="text-sm">Great job! You've earned 50 points.</p>
        </div>
        <button
          onClick={() => {
            setCurrentQuestion(0);
            setSelectedAnswer('');
            setShowResult(false);
          }}
          className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Take Another Test
        </button>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Level Assessment Test</h2>
      <div className="mb-4">
        <div className="bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
          ></div>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Question {currentQuestion + 1} of {questions.length}
        </p>
      </div>

      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          {questions[currentQuestion].question}
        </h3>
        <div className="space-y-3">
          {questions[currentQuestion].options.map((option, index) => (
            <label
              key={index}
              className="flex items-center space-x-3 cursor-pointer"
            >
              <input
                type="radio"
                name="answer"
                value={option}
                checked={selectedAnswer === option}
                onChange={(e) => setSelectedAnswer(e.target.value)}
                className="w-4 h-4 text-blue-600"
              />
              <span className="text-gray-700">{option}</span>
            </label>
          ))}
        </div>
        <button
          onClick={handleNextQuestion}
          disabled={!selectedAnswer}
          className="mt-6 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {currentQuestion < questions.length - 1 ? 'Next Question' : 'Finish Test'}
        </button>
      </div>
    </div>
  );
};

const CheckLevel = ({ user }) => {
  const levelData = {
    subject: user?.subject || 'Mathematics',
    currentLevel: 'Intermediate',
    progress: 75,
    nextLevel: 'Advanced',
    pointsToNext: 125,
    strengths: ['Algebra', 'Geometry', 'Problem Solving'],
    weaknesses: ['Calculus', 'Statistics']
  };

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-6">Your Learning Level</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Current Status</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Subject:</span>
              <span className="font-semibold">{levelData.subject}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Current Level:</span>
              <span className="font-semibold text-blue-600">{levelData.currentLevel}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Progress:</span>
              <span className="font-semibold">{levelData.progress}%</span>
            </div>
            <div className="bg-white rounded-full h-3 mt-2">
              <div 
                className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${levelData.progress}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Next Level</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Target Level:</span>
              <span className="font-semibold text-green-600">{levelData.nextLevel}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Points Needed:</span>
              <span className="font-semibold">{levelData.pointsToNext}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Current Points:</span>
              <span className="font-semibold">{user?.points || 0}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-green-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-green-800 mb-3">Strengths</h3>
          <ul className="space-y-2">
            {levelData.strengths.map((strength, index) => (
              <li key={index} className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="text-gray-700">{strength}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-red-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-red-800 mb-3">Areas for Improvement</h3>
          <ul className="space-y-2">
            {levelData.weaknesses.map((weakness, index) => (
              <li key={index} className="flex items-center space-x-2">
                <X className="w-5 h-5 text-red-600" />
                <span className="text-gray-700">{weakness}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

// Teacher Dashboard Components
const ManageStudents = ({ user }) => {
  const [students, setStudents] = useState([
    { id: 1, name: 'John Doe', email: 'john@example.com', level: 'Intermediate', status: 'pending', requestDate: '2025-07-14' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', level: 'Beginner', status: 'approved', requestDate: '2025-07-13' },
    { id: 3, name: 'Mike Johnson', email: 'mike@example.com', level: 'Advanced', status: 'pending', requestDate: '2025-07-12' },
  ]);

  const handleStatusChange = (studentId, newStatus) => {
    setStudents(students.map(student => 
      student.id === studentId ? { ...student, status: newStatus } : student
    ));
  };

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Student Management</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <h3 className="font-semibold text-blue-800">Total Students</h3>
          <p className="text-2xl font-bold text-blue-600">{students.length}</p>
        </div>
        <div className="bg-green-50 rounded-lg p-4">
          <h3 className="font-semibold text-green-800">Approved</h3>
          <p className="text-2xl font-bold text-green-600">
            {students.filter(s => s.status === 'approved').length}
          </p>
        </div>
        <div className="bg-yellow-50 rounded-lg p-4">
          <h3 className="font-semibold text-yellow-800">Pending</h3>
          <p className="text-2xl font-bold text-yellow-600">
            {students.filter(s => s.status === 'pending').length}
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {students.map((student) => (
          <div key={student.id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold text-gray-800">{student.name}</h3>
                <p className="text-gray-600">{student.email}</p>
                <p className="text-gray-600">Level: {student.level}</p>
                <p className="text-gray-600">Request Date: {student.requestDate}</p>
              </div>
              <div className="flex space-x-2">
                <span className={`px-2 py-1 rounded-full text-sm ${
                  student.status === 'approved' 
                    ? 'bg-green-100 text-green-800' 
                    : student.status === 'pending'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {student.status}
                </span>
                {student.status === 'pending' && (
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleStatusChange(student.id, 'approved')}
                      className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 transition-colors"
                    >
                      Accept
                    </button>
                    <button
                      onClick={() => handleStatusChange(student.id, 'rejected')}
                      className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 transition-colors"
                    >
                      Reject
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const ManageSchedule = ({ user }) => {
  const [schedule, setSchedule] = useState([
    { id: 1, date: '2025-07-15', time: '10:00 AM', duration: 60, available: true },
    { id: 2, date: '2025-07-16', time: '2:00 PM', duration: 60, available: true },
    { id: 3, date: '2025-07-17', time: '11:00 AM', duration: 60, available: false },
  ]);

  const [newSlot, setNewSlot] = useState({
    date: '',
    time: '',
    duration: 60
  });

  const handleAddSlot = () => {
    if (newSlot.date && newSlot.time) {
      setSchedule([...schedule, {
        id: Date.now(),
        ...newSlot,
        available: true
      }]);
      setNewSlot({ date: '', time: '', duration: 60 });
    }
  };

  const toggleAvailability = (slotId) => {
    setSchedule(schedule.map(slot => 
      slot.id === slotId ? { ...slot, available: !slot.available } : slot
    ));
  };

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Monthly Schedule</h2>
      
      <div className="bg-gray-50 rounded-lg p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Add New Time Slot</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="date"
            value={newSlot.date}
            onChange={(e) => setNewSlot({...newSlot, date: e.target.value})}
            className="p-2 border border-gray-300 rounded-lg"
          />
          <input
            type="time"
            value={newSlot.time}
            onChange={(e) => setNewSlot({...newSlot, time: e.target.value})}
            className="p-2 border border-gray-300 rounded-lg"
          />
          <select
            value={newSlot.duration}
            onChange={(e) => setNewSlot({...newSlot, duration: parseInt(e.target.value)})}
            className="p-2 border border-gray-300 rounded-lg"
          >
            <option value={30}>30 minutes</option>
            <option value={60}>60 minutes</option>
            <option value={90}>90 minutes</option>
          </select>
        </div>
        <button
          onClick={handleAddSlot}
          className="mt-4 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
        >
          Add Time Slot
        </button>
      </div>

      <div className="space-y-4">
        {schedule.map((slot) => (
          <div key={slot.id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-semibold text-gray-800">{slot.date}</h3>
                <p className="text-gray-600">{slot.time} - {slot.duration} minutes</p>
              </div>
              <div className="flex items-center space-x-4">
                <span className={`px-2 py-1 rounded-full text-sm ${
                  slot.available 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {slot.available ? 'Available' : 'Booked'}
                </span>
                <button
                  onClick={() => toggleAvailability(slot.id)}
                  className={`px-3 py-1 rounded text-sm ${
                    slot.available 
                      ? 'bg-red-600 text-white hover:bg-red-700' 
                      : 'bg-green-600 text-white hover:bg-green-700'
                  } transition-colors`}
                >
                  {slot.available ? 'Mark Unavailable' : 'Mark Available'}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const ManageDocuments = ({ user }) => {
  const [documents, setDocuments] = useState([
    { id: 1, title: 'Introduction to Algebra', type: 'PDF', uploadDate: '2025-07-10' },
    { id: 2, title: 'Geometry Basics', type: 'DOC', uploadDate: '2025-07-12' },
    { id: 3, title: 'Practice Problems', type: 'PDF', uploadDate: '2025-07-14' },
  ]);

  const [newDocument, setNewDocument] = useState({
    title: '',
    description: ''
  });

  const handleUpload = () => {
    if (newDocument.title) {
      setDocuments([...documents, {
        id: Date.now(),
        title: newDocument.title,
        type: 'PDF',
        uploadDate: new Date().toISOString().split('T')[0]
      }]);
      setNewDocument({ title: '', description: '' });
    }
  };

  const handleDelete = (docId) => {
    setDocuments(documents.filter(doc => doc.id !== docId));
  };

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Document Management</h2>
      
      <div className="bg-gray-50 rounded-lg p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Upload New Document</h3>
        <div className="space-y-4">
          <input
            type="text"
            placeholder="Document Title"
            value={newDocument.title}
            onChange={(e) => setNewDocument({...newDocument, title: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded-lg"
          />
          <textarea
            placeholder="Description (optional)"
            value={newDocument.description}
            onChange={(e) => setNewDocument({...newDocument, description: e.target.value})}
            rows="3"
            className="w-full p-2 border border-gray-300 rounded-lg"
          />
          <div className="flex items-center space-x-4">
            <input
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              className="flex-1 p-2 border border-gray-300 rounded-lg"
            />
            <button
              onClick={handleUpload}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              Upload
            </button>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {documents.map((doc) => (
          <div key={doc.id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold text-gray-800">{doc.title}</h3>
                <p className="text-gray-600">Type: {doc.type}</p>
                <p className="text-gray-600">Uploaded: {doc.uploadDate}</p>
              </div>
              <div className="flex space-x-2">
                <button className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors">
                  View
                </button>
                <button 
                  onClick={() => handleDelete(doc.id)}
                  className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default App;