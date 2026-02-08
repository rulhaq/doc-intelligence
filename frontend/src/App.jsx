import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/Layout/MainLayout';

import Dashboard from './pages/Dashboard';
import IntelligenceInsights from './pages/IntelligenceInsights';
import CaseComparison from './pages/CaseComparison';
import ChatInterface from './pages/ChatInterface';
import Login from './pages/Login';
import AdminConsole from './pages/AdminConsole';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  const handleLogin = (newToken) => {
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setToken(null);
  };

  if (!token) {
    return (
      <Router>
        <Routes>
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </Router>
    );
  }

  return (
    <Router>
      <MainLayout onLogout={handleLogout}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/intelligence" element={<IntelligenceInsights />} />
          <Route path="/comparison" element={<CaseComparison />} />
          <Route path="/chat" element={<ChatInterface />} />
          <Route path="/admin" element={<AdminConsole />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App;
