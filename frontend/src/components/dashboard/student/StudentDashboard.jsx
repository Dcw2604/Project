import React from "react";

const StudentDashboard = () => (
  <div className="min-h-screen bg-gray-50 p-8">
    <h2 className="text-2xl font-bold text-blue-700 mb-6">Student Dashboard</h2>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* Class Scheduling */}
      <div className="bg-white rounded-lg shadow-md p-6 flex flex-col">
        <h3 className="text-lg font-semibold mb-2">Class Scheduling</h3>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
          Book Class
        </button>
      </div>
      {/* AI Chatbot */}
      <div className="bg-white rounded-lg shadow-md p-6 flex flex-col">
        <h3 className="text-lg font-semibold mb-2">AI Chatbot</h3>
        <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
          Ask a Question
        </button>
      </div>
      {/* Level Assessment Test */}
      <div className="bg-white rounded-lg shadow-md p-6 flex flex-col">
        <h3 className="text-lg font-semibold mb-2">Level Assessment Test</h3>
        <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors">
          Take Test
        </button>
      </div>
      {/* Progress Tracking */}
      <div className="bg-white rounded-lg shadow-md p-6 flex flex-col col-span-1 md:col-span-2 lg:col-span-1">
        <h3 className="text-lg font-semibold mb-2">Progress Tracking</h3>
        <div className="flex items-center space-x-4">
          <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center text-2xl font-bold text-blue-700">
            85%
          </div>
          <div>
            <div className="text-gray-700">Current Level: Intermediate</div>
            <div className="text-gray-500 text-sm">Strengths: Math, Science</div>
            <div className="text-gray-500 text-sm">Weaknesses: History</div>
          </div>
        </div>
      </div>
      {/* Points System */}
      <div className="bg-white rounded-lg shadow-md p-6 flex flex-col">
        <h3 className="text-lg font-semibold mb-2">Points System</h3>
        <div className="text-3xl font-bold text-yellow-500">1200 pts</div>
        <div className="text-gray-500 text-sm">Earn points for activities!</div>
      </div>
    </div>
  </div>
);

export default StudentDashboard;
