import React from "react";

const TeacherDashboard = () => (
  <div className="min-h-screen bg-gray-50 p-8">
    <h2 className="text-2xl font-bold text-green-700 mb-6">Teacher Dashboard</h2>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* Student Request Management */}
      <div className="bg-white rounded-lg shadow-md p-6 flex flex-col">
        <h3 className="text-lg font-semibold mb-2">Student Requests</h3>
        <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
          View Requests
        </button>
      </div>
      {/* Availability Scheduling */}
      <div className="bg-white rounded-lg shadow-md p-6 flex flex-col">
        <h3 className="text-lg font-semibold mb-2">Availability Scheduling</h3>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
          Set Availability
        </button>
      </div>
      {/* Student Progress Monitoring */}
      <div className="bg-white rounded-lg shadow-md p-6 flex flex-col">
        <h3 className="text-lg font-semibold mb-2">Student Progress Monitoring</h3>
        <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors">
          View Analytics
        </button>
      </div>
      {/* Document Management */}
      <div className="bg-white rounded-lg shadow-md p-6 flex flex-col col-span-1 md:col-span-2 lg:col-span-1">
        <h3 className="text-lg font-semibold mb-2">Document Management</h3>
        <button className="bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 transition-colors">
          Upload Documents
        </button>
      </div>
    </div>
  </div>
);

export default TeacherDashboard;
