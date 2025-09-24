import React from 'react';

const App = () => {
  return (
    <div style={{ 
      padding: '20px', 
      backgroundColor: '#f0f0f0', 
      minHeight: '100vh',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{ color: '#333', marginBottom: '20px' }}>EduConnect - Test</h1>
      <p style={{ color: '#666', fontSize: '18px' }}>
        If you can see this message, React is working correctly!
      </p>
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginTop: '20px'
      }}>
        <h2 style={{ color: '#444', marginBottom: '10px' }}>Status Check:</h2>
        <ul style={{ color: '#666' }}>
          <li>✅ React is rendering</li>
          <li>✅ CSS styles are working</li>
          <li>✅ Components can be displayed</li>
        </ul>
      </div>
    </div>
  );
};

export default App;
