import React from "react";

const TeacherAuth = () => (
  <div className="max-w-md mx-auto mt-12 bg-white p-8 rounded-lg shadow-md">
    <h2 className="text-2xl font-bold text-green-700 mb-6">Teacher Login</h2>
    {/* TODO: Add login form and registration link */}
    <form>
      <input type="email" placeholder="Email" className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500" />
      <input type="password" placeholder="Password" className="w-full p-3 mb-6 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500" />
      <button type="submit" className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors">Login</button>
    </form>
    <div className="mt-4 text-center">
      <a href="/register/teacher" className="text-green-600 hover:underline">Create a teacher account</a>
    </div>
  </div>
);

export default TeacherAuth;
