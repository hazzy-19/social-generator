import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, signInWithGoogle, signInAnonymously, currentUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (currentUser) {
      navigate('/settings');
    }
  }, [currentUser, navigate]);

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      setError('');
      setLoading(true);
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError('Failed to log in: ' + err.message);
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
      setError('Failed to log in with Google: ' + err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleGuestSignIn() {
    try {
      setError('');
      setLoading(true);
      await signInAnonymously();
      navigate('/');
    } catch (err) {
      setError('Failed to continue as guest: ' + err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-background text-on-background min-h-screen flex flex-col items-center justify-center font-body-md text-body-md antialiased selection:bg-primary-container selection:text-on-primary relative">
      {/* Back Button */}
      <button 
        onClick={() => navigate(-1)}
        className="absolute top-6 left-6 flex items-center gap-2 text-on-surface-variant hover:text-primary transition-colors font-label-md"
      >
        <span className="material-symbols-outlined">arrow_back</span>
        Back
      </button>

      {/* Main Container */}
      <main className="w-full max-w-md px-margin-mobile md:px-0 mt-12">
        {/* Header Wordmark */}
        <header className="text-center mb-12">
          <h1 className="font-display-lg text-display-lg text-primary tracking-tight">Social Generator</h1>
        </header>

        {/* Auth Card */}
        <section className="bg-surface-container-lowest border border-outline-variant/30 rounded-lg p-8 md:p-12">
          {/* Headline */}
          <div className="mb-8 text-center">
            <h2 className="font-headline-lg text-headline-lg text-on-surface mb-2">Welcome Back</h2>
            <p className="font-body-md text-body-md text-on-surface-variant">Please enter your details to sign in.</p>
          </div>

          {error && <div className="mb-4 p-3 bg-error-container text-on-error-container rounded text-center">{error}</div>}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Google Button */}
            <button onClick={handleGoogleSignIn} disabled={loading} className="w-full py-3 px-4 bg-surface border border-outline-variant text-on-surface font-label-md text-label-md rounded-full hover:bg-surface-variant transition-colors duration-200 flex justify-center items-center gap-2 disabled:opacity-50" type="button">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"></path>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"></path>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"></path>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"></path>
              </svg>
              Sign in with Google
            </button>

            {/* Guest Button */}
            <button 
              onClick={handleGuestSignIn} 
              disabled={loading}
              className="w-full py-3 px-4 bg-transparent border border-outline-variant text-on-surface font-label-md text-label-md rounded-full hover:bg-surface-variant transition-colors duration-200 flex justify-center items-center gap-2 disabled:opacity-50" 
              type="button"
            >
              <span className="material-symbols-outlined">person</span>
              Continue as Guest
            </button>

            {/* Divider */}
            <div className="relative flex items-center py-2">
              <div className="flex-grow border-t border-outline-variant/30"></div>
              <span className="flex-shrink-0 mx-4 font-label-sm text-label-sm text-on-surface-variant">or continue with email</span>
              <div className="flex-grow border-t border-outline-variant/30"></div>
            </div>

            {/* Email Field */}
            <div>
              <label className="block font-label-md text-label-md text-on-surface mb-2" htmlFor="email">Email</label>
              <input 
                className="w-full px-4 py-3 bg-surface border border-outline-variant rounded focus:border-primary focus:ring-0 focus:outline-none transition-colors duration-200 font-body-md text-body-md text-on-surface placeholder-on-surface-variant/50" 
                id="email" 
                name="email" 
                placeholder="name@example.com" 
                required 
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            {/* Password Field */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block font-label-md text-label-md text-on-surface" htmlFor="password">Password</label>
                <a className="font-label-sm text-label-sm text-on-surface-variant hover:text-primary transition-colors duration-200" href="#">Forgot password?</a>
              </div>
              <input 
                className="w-full px-4 py-3 bg-surface border border-outline-variant rounded focus:border-primary focus:ring-0 focus:outline-none transition-colors duration-200 font-body-md text-body-md text-on-surface placeholder-on-surface-variant/50" 
                id="password" 
                name="password" 
                placeholder="••••••••" 
                required 
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            {/* Sign In Button */}
            <button 
              disabled={loading}
              className="w-full py-3 px-4 bg-primary-container text-on-primary font-label-md text-label-md rounded-full hover:bg-primary transition-colors duration-200 flex justify-center items-center disabled:opacity-50" 
              type="submit"
            >
              Sign In
            </button>
          </form>
        </section>

        {/* Footer Link */}
        <div className="mt-8 text-center">
          <p className="font-body-md text-body-md text-on-surface-variant">
            Don't have an account? 
            <Link className="font-label-md text-label-md text-primary hover:underline transition-all ml-1" to="/signup">Sign Up</Link>
          </p>
        </div>
      </main>
    </div>
  );
}
