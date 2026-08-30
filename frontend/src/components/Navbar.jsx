import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Navbar() {
  const { logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Failed to log out', error);
    }
  };

  return (
    <header className="bg-surface w-full top-0 sticky border-b border-outline-variant flex justify-between items-center h-16 px-margin-desktop max-w-container-max mx-auto mb-12 z-50 bg-white/80 backdrop-blur-sm shadow-sm border-surface-dim">
      <div className="font-headline-md text-headline-md font-semibold text-primary" style={{ color: '#002627' }}>
        Social Generator
      </div>
      <nav className="hidden md:flex gap-8">
        <Link to="/" className={`${location.pathname === '/' ? 'text-primary border-b-2 border-primary pb-1' : 'text-on-surface-variant hover:text-primary'} font-label-md text-label-md transition-colors duration-200 cursor-pointer transition-all active:opacity-70`}>
          Generator
        </Link>
        <Link to="/history" className={`${location.pathname === '/history' ? 'text-primary border-b-2 border-primary pb-1' : 'text-on-surface-variant hover:text-primary'} font-label-md text-label-md transition-colors duration-200 cursor-pointer transition-all active:opacity-70`}>
          History
        </Link>
        <a className="text-on-surface-variant hover:text-primary font-label-md text-label-md transition-colors duration-200 cursor-pointer transition-all active:opacity-70" href="#">
          Library
        </a>
      </nav>
      <div className="flex gap-4">
        <Link to="/profile" className="text-on-surface-variant hover:text-primary transition-colors duration-200 cursor-pointer active:opacity-70">
          <span className="material-symbols-outlined">settings</span>
        </Link>
        <button onClick={handleLogout} className="text-on-surface-variant hover:text-primary transition-colors duration-200 cursor-pointer active:opacity-70" title="Logout">
          <span className="material-symbols-outlined">account_circle</span>
        </button>
      </div>
    </header>
  );
}
