import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { useAuth } from '../contexts/AuthContext';

const API = 'http://127.0.0.1:8000';

export default function History() {
  const { currentUser } = useAuth();
  const [generations, setGenerations] = useState([]);
  const [search, setSearch] = useState('');
  const [platformFilter, setPlatformFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchGenerations = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (platformFilter) params.set('platform', platformFilter);
      if (search) params.set('search', search);
      
      const headers = {};
      if (currentUser) {
        const token = await currentUser.getIdToken();
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const res = await fetch(`${API}/generations?${params}`, { headers });
      if (res.ok) {
        setGenerations(await res.json());
      }
    } catch (err) {
      console.error('Failed to fetch generations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (currentUser) {
      fetchGenerations();
    } else {
      setLoading(false);
    }
  }, [platformFilter, currentUser]);

  // Debounced search
  useEffect(() => {
    if (!currentUser) return;
    const timer = setTimeout(() => fetchGenerations(), 400);
    return () => clearTimeout(timer);
  }, [search]);

  const timeAgo = (dateStr) => {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    if (days < 30) return `${days}d ago`;
    return new Date(dateStr).toLocaleDateString();
  };

  const statusColor = {
    draft: 'bg-[#f59e0b]',
    ready: 'bg-[#3b82f6]',
    saved: 'bg-[#10b981]',
  };

  const statusLabel = {
    draft: 'Draft',
    ready: 'Ready',
    saved: 'Saved',
  };

  const handleRestore = (gen) => {
    // Navigate to dashboard and pass generation data via state
    navigate('/', { state: { generation: gen } });
  };

  const handleDownload = (gen) => {
    const text = `${gen.caption || ''}\n\n${(gen.hashtags || []).join(' ')}`;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${gen.platform}_post_${gen.id.slice(0, 8)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };
  
  const getFullImageUrl = (url) => {
    if (!url) return '';
    if (url.startsWith('http')) return url;
    return `http://127.0.0.1:8000${url}`;
  };

  return (
    <div className="bg-surface-container-low min-h-screen flex flex-col font-body-md text-on-surface">
      <Navbar />
      
      <main className="flex-grow w-full max-w-[900px] mx-auto px-4 md:px-0 py-12">
        <div className="bg-surface border border-outline-variant rounded-lg">
          {/* Header */}
          <div className="p-6 border-b border-outline-variant flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <h1 className="font-headline-lg text-headline-lg text-primary">Past Generations</h1>
            <div className="flex items-center gap-4 w-full md:w-auto">
              <div className="relative w-full md:w-64">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline-variant text-sm">search</span>
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-outline-variant rounded bg-surface focus:outline-none focus:border-primary focus:ring-0 font-body-md text-body-md placeholder-outline"
                  placeholder="Search past posts..."
                  type="text"
                />
              </div>
              <select
                value={platformFilter}
                onChange={(e) => setPlatformFilter(e.target.value)}
                className="border border-outline-variant rounded px-4 py-2 bg-surface focus:outline-none focus:border-primary font-body-md text-body-md"
              >
                <option value="">All Platforms</option>
                <option value="instagram">Instagram</option>
                <option value="linkedin">LinkedIn</option>
                <option value="x">X</option>
                <option value="facebook">Facebook</option>
              </select>
            </div>
          </div>
          
          {/* List */}
          <div className="flex flex-col">
            {loading ? (
              <div className="p-12 text-center text-on-surface-variant font-body-md">Loading...</div>
            ) : !currentUser ? (
              <div className="p-12 text-center flex flex-col items-center gap-3">
                <p className="font-body-md text-on-surface-variant">Please log in to view your generations.</p>
              </div>
            ) : generations.length === 0 ? (
              <div className="p-12 text-center flex flex-col items-center gap-3">
                <span className="material-symbols-outlined text-[48px] text-outline-variant">history</span>
                <p className="font-body-md text-on-surface-variant">No generations yet. Create your first post!</p>
              </div>
            ) : (
              generations.map((gen) => (
                <div key={gen.id} className="flex flex-col md:flex-row items-start md:items-center p-6 border-b border-outline-variant hover:bg-surface-container-lowest transition-colors gap-4 md:gap-6">
                  {/* Thumbnail */}
                  {gen.image_url ? (
                    <img
                      alt="Thumbnail"
                      className="w-20 h-20 object-cover rounded border border-outline-variant shrink-0"
                      src={getFullImageUrl(gen.image_url)}
                    />
                  ) : (
                    <div className="w-20 h-20 rounded border border-outline-variant bg-surface-container-high flex items-center justify-center text-on-surface-variant shrink-0">
                      <span className="material-symbols-outlined text-[24px]">article</span>
                    </div>
                  )}

                  {/* Info */}
                  <div className="flex-grow min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="bg-primary-container text-on-primary-container font-label-sm text-label-sm px-2 py-0.5 rounded-full capitalize">
                        {gen.platform}
                      </span>
                      <span className="text-outline font-label-sm text-label-sm">{timeAgo(gen.created_at)}</span>
                      <div className="flex items-center gap-1">
                        <span className={`w-2 h-2 rounded-full ${statusColor[gen.status] || 'bg-outline'}`}></span>
                        <span className="text-outline font-label-sm text-label-sm">{statusLabel[gen.status] || gen.status}</span>
                      </div>
                    </div>
                    <p className="font-body-md text-body-md text-on-surface truncate">
                      {gen.caption || 'No caption'}
                    </p>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-3 shrink-0 mt-2 md:mt-0">
                    <button
                      onClick={() => handleDownload(gen)}
                      className="p-2 border border-outline-variant rounded-full text-on-surface-variant hover:text-primary hover:border-primary transition-colors"
                      title="Download"
                    >
                      <span className="material-symbols-outlined text-[18px]">download</span>
                    </button>
                    <button
                      onClick={() => handleRestore(gen)}
                      className="font-label-sm text-label-sm text-primary underline hover:opacity-70 transition-opacity whitespace-nowrap"
                    >
                      Restore
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </main>
      
      {/* Footer */}
      <footer className="bg-surface w-full py-8 mt-auto border-t border-outline-variant">
        <div className="flex flex-col md:flex-row justify-between items-center px-8 max-w-[900px] mx-auto gap-4">
          <div className="font-label-md text-label-md font-bold text-primary">
            © 2024 Social Generator
          </div>
        </div>
      </footer>
    </div>
  );
}
