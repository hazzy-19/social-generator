import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

export default function Signup() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { signup, signInWithGoogle } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      setError('');
      setLoading(true);
      await signup(email, password);
      navigate('/');
    } catch (err) {
      setError('Failed to create an account: ' + err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleSignIn() {
    try {
      setError('');
      setLoading(true);
      await signInWithGoogle();
      navigate('/');
    } catch (err) {
      setError('Failed to sign up with Google: ' + err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-background">
      <div className="w-full max-w-md bg-surface-container-lowest border border-outline-variant/30 rounded-lg shadow-sm p-8 md:p-12">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="font-headline-lg text-headline-lg text-primary mb-2">The Quiet Authority</h1>
          <p className="font-headline-md text-headline-md text-on-surface">Create your account</p>
        </div>
        
        {error && <div className="mb-4 p-3 bg-error-container text-on-error-container rounded text-center">{error}</div>}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <div>
              <label className="block font-label-md text-label-md text-on-surface-variant mb-1" htmlFor="fullName">Full Name</label>
              <input 
                className="w-full border border-outline-variant rounded-lg px-4 py-3 font-body-md text-body-md text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors bg-transparent placeholder:text-outline-variant/70" 
                id="fullName" 
                placeholder="Jane Doe" 
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
            <div>
              <label className="block font-label-md text-label-md text-on-surface-variant mb-1" htmlFor="email">Email</label>
              <input 
                className="w-full border border-outline-variant rounded-lg px-4 py-3 font-body-md text-body-md text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors bg-transparent placeholder:text-outline-variant/70" 
                id="email" 
                placeholder="jane@example.com" 
                required 
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label className="block font-label-md text-label-md text-on-surface-variant mb-1" htmlFor="password">Password</label>
              <input 
                className="w-full border border-outline-variant rounded-lg px-4 py-3 font-body-md text-body-md text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors bg-transparent placeholder:text-outline-variant/70" 
                id="password" 
                placeholder="••••••••" 
                required 
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>
          
          <div className="pt-2">
            <button 
              disabled={loading}
              className="w-full bg-primary-container text-on-primary rounded-full py-3 font-label-md text-label-md hover:bg-primary transition-colors disabled:opacity-50" 
              type="submit"
            >
              Create Account
            </button>
          </div>
        </form>

        <div className="my-8 flex items-center justify-center space-x-4">
          <div className="h-px bg-outline-variant/50 flex-grow"></div>
          <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Or</span>
          <div className="h-px bg-outline-variant/50 flex-grow"></div>
        </div>

        {/* Secondary Action */}
        <button onClick={handleGoogleSignIn} disabled={loading} className="w-full border border-outline-variant rounded-full py-3 flex items-center justify-center space-x-2 hover:bg-surface-container-low transition-colors text-on-surface font-label-md text-label-md disabled:opacity-50" type="button">
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"></path>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"></path>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"></path>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"></path>
          </svg>
          <span>Sign up with Google</span>
        </button>
        
        {/* Guest Button */}
        <button 
          onClick={() => navigate('/')}
          className="mt-4 w-full border border-outline-variant rounded-full py-3 flex items-center justify-center space-x-2 hover:bg-surface-container-low transition-colors text-on-surface font-label-md text-label-md" 
          type="button"
        >
          <span className="material-symbols-outlined">person</span>
          <span>Continue as Guest</span>
        </button>

        {/* Footer */}
        <div className="mt-8 text-center">
          <Link className="font-body-md text-body-md text-on-surface-variant hover:text-primary transition-colors border-b border-transparent hover:border-primary pb-0.5" to="/login">
            Already have an account? Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}
