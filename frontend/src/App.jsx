import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import Profile from './pages/Profile';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          
          <Route 
            path="/" 
            element={<Dashboard />} 
          />
          <Route 
            path="/history" 
            element={<History />} 
          />
          <Route 
            path="/profile" 
            element={<Profile />} 
          />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
