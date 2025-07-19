import React from "react";

const TeacherDashboard = () => (
  <div className="min-h-screen bg-gray-50 p-8">
    <h2 className="text-2xl font-bold text-green-700 mb-6">Teacher Dashboard</h2>
    {/* TODO: Add request management, availability, progress monitoring, document management */}
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">Student Request Management (Coming Soon)</div>
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">Availability Scheduling (Coming Soon)</div>
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">Student Progress Monitoring (Coming Soon)</div>
    <div className="bg-white rounded-lg shadow-md p-6">Document Management (Coming Soon)</div>
  </div>
);

export default TeacherDashboard;
