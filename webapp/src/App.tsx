import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AuthPage from './pages/AuthPage';
import MainPage from './pages/MainPage'; // We will move your existing App UI here
import DashboardPage from "./pages/DashboardPage";
import ConversePage from "./pages/ConversePage";


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/main" element={<MainPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/converse/:id" element={<ConversePage />} /> {/* Add this */}


        {/* Redirect unknown routes to home or auth */}
        <Route path="/" element={<Navigate to="/auth" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
