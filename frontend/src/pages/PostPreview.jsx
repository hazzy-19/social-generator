import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Navbar';

export default function PostPreview() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { getAuthHeaders } = useAuth();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [platform, setPlatform] = useState('');
  const [caption, setCaption] = useState('');
  const [hashtags, setHashtags] = useState([]);
  const [imageUrl, setImageUrl] = useState('');
  const [status, setStatus] = useState('');
  
  useEffect(() => {
    fetchGeneration();
  }, [id]);

  const fetchGeneration = async () => {
    setLoading(true);
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`http://127.0.0.1:8000/generations/${id}`, {
        headers
      });
      
      if (!response.ok) {
        if (response.status === 404) {
          navigate('/history');
          return;
        }
        throw new Error('Failed to fetch post');
      }
      
      const data = await response.json();
      setPlatform(data.platform);
      setCaption(data.caption || '');
      setHashtags(data.hashtags || []);
      setImageUrl(data.image_url || '');
      setStatus(data.status);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`http://127.0.0.1:8000/generations/${id}/save`, {
        method: 'POST',
        headers: {
          ...headers,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          caption,
          hashtags
        })
      });
      
      if (!response.ok) throw new Error("Failed to save generation");
      navigate('/history');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to delete this post?")) return;
    
    setLoading(true);
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`http://127.0.0.1:8000/generations/${id}`, {
        method: 'DELETE',
        headers
      });
      
      if (!response.ok) throw new Error("Failed to delete post");
      navigate('/history');
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const getFullImageUrl = (url) => {
    if (!url) return '';
    if (url.startsWith('http')) return url;
    return `http://127.0.0.1:8000${url}`;
  };

  if (loading && !caption && !imageUrl) {
    return (
      <div className="bg-surface-container-low min-h-screen flex flex-col font-body-md text-on-surface">
        <Navbar />
        <main className="flex-grow flex items-center justify-center">
          <div className="font-body-md text-primary animate-pulse flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">sync</span>
            Loading post...
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="bg-surface-container-low min-h-screen flex flex-col font-body-md text-on-surface">
      <Navbar />
      
      <main className="flex-grow w-full max-w-[900px] mx-auto px-4 md:px-0 pt-6 pb-12 flex flex-col gap-8">
        <div className="flex items-center justify-between">
          <button 
            onClick={() => navigate('/history')}
            className="flex items-center gap-2 text-on-surface-variant hover:text-primary transition-colors font-label-md"
          >
            <span className="material-symbols-outlined">arrow_back</span>
            Back to History
          </button>
          
          <button 
            onClick={handleDelete}
            className="flex items-center gap-2 text-error hover:text-error-container transition-colors font-label-md px-4 py-2 rounded-full border border-error/30 hover:bg-error/10"
          >
            <span className="material-symbols-outlined text-[18px]">delete</span>
            Delete Post
          </button>
        </div>

        {error && (
          <div className="p-4 bg-error-container text-on-error-container rounded font-body-md">
            {error}
          </div>
        )}

        <div className="bg-surface border border-outline-variant rounded p-8">
          <div className="flex items-center gap-3 mb-8">
            <h1 className="font-headline-md text-headline-md text-on-surface">Post Preview</h1>
            <span className="bg-primary-container text-on-primary-container font-label-sm px-2 py-0.5 rounded-full capitalize">
              {platform}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
            {/* LEFT COLUMN (Image) */}
            <div className="md:col-span-5 flex flex-col gap-4">
              <div className="w-full aspect-[4/3] rounded border border-outline-variant overflow-hidden bg-surface-container-lowest">
                {imageUrl ? (
                  <img alt="Post graphic" className="w-full h-full object-cover" src={getFullImageUrl(imageUrl)} />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-on-surface-variant">No Image</div>
                )}
              </div>
            </div>

            {/* RIGHT COLUMN (Caption & Hashtags) */}
            <div className="md:col-span-7 flex flex-col gap-6">
              <div className="flex flex-col gap-2">
                <label className="font-label-md text-primary">Caption</label>
                <textarea 
                  value={caption}
                  onChange={(e) => setCaption(e.target.value)}
                  className="w-full bg-surface border border-outline-variant rounded p-4 font-body-md text-on-surface focus:border-primary focus:ring-0 transition-colors resize-y" 
                  rows="8"
                />
              </div>

              <div className="flex flex-col gap-3">
                <label className="font-label-md text-primary uppercase text-[12px] tracking-wider">Hashtags</label>
                <div className="flex flex-wrap gap-2">
                  {(hashtags || []).map((tag, idx) => (
                    <span key={idx} className="px-3 py-1 bg-primary-fixed text-on-primary-fixed-variant rounded-full font-label-sm">
                      {tag.startsWith('#') ? tag : `#${tag}`}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex flex-col gap-4 mt-4">
                <button 
                  onClick={() => navigator.clipboard.writeText(caption)}
                  className="w-full bg-surface-container text-on-surface font-label-md py-3 rounded-full hover:bg-surface-container-highest transition-colors"
                >
                  Copy Caption
                </button>
                <button 
                  onClick={handleSave} 
                  disabled={loading} 
                  className="w-full bg-primary text-on-primary font-label-md py-3 rounded-full hover:opacity-90 transition-opacity flex justify-center items-center gap-2"
                >
                  <span className="material-symbols-outlined">save</span> 
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
