import React from "react";

const Header = () => (
  <header className="bg-white shadow-md py-4 px-6 flex items-center justify-between">
    <div className="text-2xl font-bold text-blue-700">EduConnect</div>
    <nav className="space-x-4">
      <a href="/" className="text-gray-700 hover:text-blue-600">Home</a>
      <a href="/login/student" className="text-gray-700 hover:text-blue-600">Student Login</a>
      <a href="/login/teacher" className="text-gray-700 hover:text-blue-600">Teacher Login</a>
    </nav>
  </header>
);

export default Header;
