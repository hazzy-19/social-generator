import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { useAuth } from '../contexts/AuthContext';

function useSessionState(key, initialValue) {
  const [state, setState] = useState(() => {
    try {
      const stored = sessionStorage.getItem(key);
      return stored !== null ? JSON.parse(stored) : initialValue;
    } catch (e) {
      return initialValue;
    }
  });
  useEffect(() => {
    sessionStorage.setItem(key, JSON.stringify(state));
  }, [key, state]);
  return [state, setState];
}

export default function Dashboard() {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const [topic, setTopic] = useSessionState('dashboard_topic', '');
  const [platform, setPlatform] = useSessionState('dashboard_platform', 'linkedin');
  const [loading, setLoading] = useState(false);
  
  const [caption, setCaption] = useSessionState('dashboard_caption', '');
  const [hashtags, setHashtags] = useSessionState('dashboard_hashtags', []);
  const [imageUrl, setImageUrl] = useSessionState('dashboard_imageUrl', '');
  
  const [generationId, setGenerationId] = useSessionState('dashboard_generationId', null);
  const [imageApproved, setImageApproved] = useSessionState('dashboard_imageApproved', false);
  const [captionApproved, setCaptionApproved] = useSessionState('dashboard_captionApproved', false);
  const [hashtagsApproved, setHashtagsApproved] = useSessionState('dashboard_hashtagsApproved', false);

  const platforms = [
    { id: 'instagram', label: 'Instagram' },
    { id: 'linkedin', label: 'LinkedIn' },
    { id: 'x', label: 'X' },
    { id: 'facebook', label: 'Facebook' },
  ];

  const [error, setError] = useState('');

  const getAuthHeaders = async () => {
    if (!currentUser) {
      await logout();
      navigate('/login');
      throw new Error("Session expired. Please log in again.");
    }
    try {
      const token = await currentUser.getIdToken();
      return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };
    } catch (err) {
      await logout();
      navigate('/login');
      throw new Error("Session expired. Please log in again.");
    }
  };

  const [optimizing, setOptimizing] = useState(false);

  const handleOptimize = async () => {
    if (!topic) return;
    setOptimizing(true);
    setError('');
    
    try {
      const headers = await getAuthHeaders();
      const response = await fetch('http://127.0.0.1:8000/generations/optimize-source', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          source_content: topic,
          platform: platform
        }),
      });
      
      if (!response.ok) {
        let errorMsg = "Failed to optimize";
        try {
            const data = await response.json();
            errorMsg = data.detail || errorMsg;
        } catch (e) {}
        throw new Error(errorMsg);
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        buffer = lines.pop();
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.substring(6);
            if (!dataStr.trim()) continue;
            
            try {
              const data = JSON.parse(dataStr);
              if (data.status === 'error') {
                setError(data.message);
              } else if (data.status === 'complete') {
                setTopic(data.data.optimized_content);
              }
            } catch (e) {
              console.error("Error parsing stream chunk:", e, dataStr);
            }
          }
        }
      }
    } catch (error) {
      console.error("Error during optimization:", error);
      setError(error.message || "We are currently experiencing issues reaching the AI model.");
    } finally {
      setOptimizing(false);
    }
  };

  const [generationStatus, setGenerationStatus] = useState('');

  const handleGenerate = async () => {
    if (!topic) return;
    setLoading(true);
    setError('');
    setGenerationStatus('Connecting to server...');
    
    try {
      const headers = await getAuthHeaders();
      const response = await fetch('http://127.0.0.1:8000/generations', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          source_content: topic,
          platform: platform
        })
      });
      
      if (!response.ok) {
        let errorMsg = "Failed to generate";
        try {
            const data = await response.json();
            errorMsg = data.detail || errorMsg;
        } catch (e) {}
        throw new Error(errorMsg);
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        buffer = lines.pop();
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.substring(6);
            if (!dataStr.trim()) continue;
            
            try {
              const data = JSON.parse(dataStr);
              if (data.status === 'error') {
                setError(data.message);
                setGenerationStatus('');
              } else if (data.status === 'thinking') {
                setGenerationStatus('Thinking...');
              } else if (data.status === 'complete') {
                setGenerationId(data.data.id);
                setCaption(data.data.caption);
                setHashtags(data.data.hashtags);
                setImageUrl(data.data.image_url);
                setImageApproved(data.data.image_approved);
                setCaptionApproved(data.data.caption_approved);
                setHashtagsApproved(data.data.hashtags_approved);
                setGenerationStatus('');
              } else if (data.status === 'prompt_ready') {
                // Ignore prompt_ready, do not show raw AI prompt in UI
              } else {
                setGenerationStatus(data.message);
              }
            } catch (e) {
              console.error("Error parsing stream chunk:", e, dataStr);
            }
          }
        }
      }
    } catch (error) {
      console.error("Error during generation:", error);
      setError(error.message || "We are currently experiencing issues reaching the AI model.");
    } finally {
      setLoading(false);
      setGenerationStatus('');
    }
  };

  const handleReload = async (section) => {
    if (!generationId) return;
    setLoading(true);
    setError('');
    
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`http://127.0.0.1:8000/generations/${generationId}/reload/${section}`, {
        method: 'POST',
        headers
      });
      
      if (!response.ok) throw new Error("Failed to reload " + section);
      const data = await response.json();
      
      if (section === 'caption') setCaption(data.caption);
      if (section === 'hashtags') setHashtags(data.hashtags);
      if (section === 'image') setImageUrl(data.image_url);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (section) => {
    if (!generationId) return;
    setLoading(true);
    
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`http://127.0.0.1:8000/generations/${generationId}/approve/${section}`, {
        method: 'POST',
        headers
      });
      
      if (!response.ok) throw new Error("Failed to approve " + section);
      
      if (section === 'caption') setCaptionApproved(true);
      if (section === 'hashtags') setHashtagsApproved(true);
      if (section === 'image') setImageApproved(true);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!generationId) return;
    setLoading(true);
    
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`http://127.0.0.1:8000/generations/${generationId}/save`, {
        method: 'POST',
        headers
      });
      
      if (!response.ok) throw new Error("Failed to save generation");
      navigate('/history');
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const getFullImageUrl = (url) => {
    if (!url) return '';
    if (url.startsWith('http')) return url;
    return `http://127.0.0.1:8000${url}`;
  };

  return (
    <div className="bg-surface-container-low min-h-screen flex flex-col font-body-md text-on-surface">
      <Navbar />
      
      <main className="flex-grow w-full max-w-[900px] mx-auto px-4 md:px-0 pt-6 pb-12 flex flex-col gap-8">
        {/* SECTION 1: Generator Card */}
        <section className="bg-surface border border-outline-variant rounded p-8 flex flex-col gap-8">
          {/* Header */}
          <div className="flex flex-col gap-2">
            <h1 className="font-headline-lg text-headline-lg text-primary">Social Generator</h1>
            <p className="font-body-md text-body-md text-on-surface-variant">Paste or write source content, then generate a platform-ready post.</p>
          </div>

          {/* Platform Tabs */}
          <div className="flex flex-col gap-2">
            <label className="font-label-md text-label-md text-primary">Target Platform</label>
            <div className="flex flex-wrap gap-2 p-1 bg-surface-container-low rounded inline-flex w-fit">
              {platforms.map(p => (
                <button 
                  key={p.id}
                  onClick={() => setPlatform(p.id)}
                  className={`px-6 py-2 rounded font-label-md text-label-md transition-colors ${
                    platform === p.id 
                    ? 'bg-surface border border-outline-variant shadow-sm text-primary' 
                    : 'text-on-surface-variant hover:text-primary'
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Source Input */}
          <div className="flex flex-col gap-2">
            <label className="font-label-md text-label-md text-primary">Source Content</label>
            <textarea 
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="w-full bg-surface border border-outline-variant rounded p-4 font-body-md text-body-md text-on-surface focus:border-primary focus:ring-0 transition-colors resize-none" 
              placeholder="Paste your text or notes here..." 
              rows="4"
            ></textarea>
            {error && (
              <div className="p-3 bg-red-50 text-red-600 rounded font-label-md text-label-md border border-red-200">
                {error}
              </div>
            )}
            <div className="flex gap-4 mt-2 items-center">
              <button 
                onClick={handleGenerate} 
                disabled={loading || optimizing}
                className="w-fit bg-primary-container text-on-primary font-label-md text-label-md py-2 px-6 rounded hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                {loading ? 'Generating...' : 'Generate'}
              </button>
              <button 
                onClick={handleOptimize} 
                disabled={loading || optimizing}
                className="w-fit border border-primary text-primary font-label-md text-label-md py-2 px-6 rounded hover:bg-surface-container-low transition-colors disabled:opacity-50"
              >
                {optimizing ? 'Optimizing...' : 'Optimize Input'}
              </button>
              {loading && generationStatus && (
                <div className="ml-4 font-body-md text-primary flex items-center gap-2 animate-pulse">
                  <span className="material-symbols-outlined text-[18px]">sync</span>
                  {generationStatus}
                </div>
              )}
            </div>
          </div>

          {/* Two-Column Layout */}
          {(caption || imageUrl) && (
            <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
              {/* LEFT COLUMN (Image) */}
              <div className="md:col-span-5 flex flex-col gap-4">
                {/* Image Actions */}
                <div className="flex justify-end items-center gap-2">
                  <button onClick={() => handleApprove('image')} disabled={loading} className={`flex items-center gap-2 px-4 py-2 border rounded-full font-label-sm text-label-sm transition-colors ${imageApproved ? 'bg-primary text-on-primary border-primary' : 'border-primary text-primary hover:bg-surface-container-low'}`}>
                    <span className="material-symbols-outlined text-[16px]">check</span> {imageApproved ? 'Approved' : 'Approve'}
                  </button>
                  <button onClick={() => handleReload('image')} disabled={loading} className="p-2 border border-outline-variant rounded-full text-on-surface-variant hover:text-primary hover:border-primary transition-colors flex items-center justify-center">
                    <span className="material-symbols-outlined text-[18px]">refresh</span>
                  </button>
                </div>
                {/* Image Preview */}
                <div className="w-full aspect-[4/3] rounded border border-outline-variant overflow-hidden relative">
                  {imageUrl ? (
                    <img alt="Generated post graphic" className="w-full h-full object-cover transition-opacity duration-300" src={getFullImageUrl(imageUrl)} />
                  ) : (
                    <div className="w-full h-full bg-surface-container-lowest flex items-center justify-center text-on-surface-variant">No Image</div>
                  )}
                </div>
              </div>

              {/* RIGHT COLUMN (Caption & Hashtags) */}
              <div className="md:col-span-7 flex flex-col gap-6">
                {/* Caption Header & Actions */}
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-4">
                    <label className="font-label-md text-label-md text-primary">Caption</label>
                    <button onClick={() => handleReload('caption')} disabled={loading} className="font-label-sm text-label-sm text-primary underline hover:opacity-70 transition-opacity">Regenerate</button>
                  </div>
                  <div className="flex items-center gap-2">
                    <button onClick={() => handleApprove('caption')} disabled={loading} className={`flex items-center gap-2 px-3 py-1.5 border rounded-full font-label-sm text-label-sm transition-colors ${captionApproved ? 'bg-primary text-on-primary border-primary' : 'border-primary text-primary hover:bg-surface-container-low'}`}>
                      <span className="material-symbols-outlined text-[16px]">check</span> {captionApproved ? 'Approved' : 'Approve'}
                    </button>
                    <button onClick={() => handleReload('caption')} disabled={loading} className="p-1.5 border border-outline-variant rounded-full text-on-surface-variant hover:text-primary hover:border-primary transition-colors flex items-center justify-center">
                      <span className="material-symbols-outlined text-[16px]">refresh</span>
                    </button>
                  </div>
                </div>

                {/* Caption Textarea */}
                <textarea 
                  value={caption}
                  onChange={(e) => setCaption(e.target.value)}
                  className="w-full bg-surface border border-outline-variant rounded p-4 font-body-md text-body-md text-on-surface focus:border-primary focus:ring-0 transition-colors resize-y" 
                  rows="6"
                />

                {/* Character Count */}
                <div className="text-right font-label-sm text-label-sm text-on-surface-variant">
                  {caption.length} / {platform === 'x' ? 280 : 2200}
                </div>

                {/* Hashtags Section */}
                <div className="flex flex-col gap-3">
                  <div className="flex justify-between items-center">
                    <label className="font-label-md text-label-md text-primary uppercase text-[12px] tracking-wider">HASHTAGS</label>
                    <div className="flex items-center gap-2">
                      <button onClick={() => handleApprove('hashtags')} disabled={loading} className={`flex items-center gap-2 px-3 py-1.5 border rounded-full font-label-sm text-label-sm transition-colors ${hashtagsApproved ? 'bg-primary text-on-primary border-primary' : 'border-outline-variant text-on-surface-variant hover:text-primary hover:border-primary'}`}>
                        <span className="material-symbols-outlined text-[16px]">check</span> {hashtagsApproved ? 'Approved' : 'Approve'}
                      </button>
                      <button onClick={() => handleReload('hashtags')} disabled={loading} className="p-1.5 border border-outline-variant rounded-full text-on-surface-variant hover:text-primary hover:border-primary transition-colors flex items-center justify-center">
                        <span className="material-symbols-outlined text-[16px]">refresh</span>
                      </button>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {(hashtags || []).map((tag, idx) => (
                      <span key={idx} className="px-3 py-1 bg-primary-fixed text-on-primary-fixed-variant rounded-full font-label-sm text-label-sm">
                        {tag.startsWith('#') ? tag : `#${tag}`}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Primary Actions */}
                <div className="flex flex-col gap-4 mt-2">
                  <button 
                    onClick={() => navigator.clipboard.writeText(caption)}
                    className="w-full bg-primary-container text-on-primary font-label-md text-label-md py-3 rounded-full hover:opacity-90 transition-opacity"
                  >
                    Copy Caption
                  </button>
                  <div className="grid grid-cols-2 gap-4">
                    <button className="w-full border border-primary text-primary font-label-md text-label-md py-3 rounded-full hover:bg-surface-container-low transition-colors flex justify-center items-center gap-2">
                      <span className="material-symbols-outlined">download</span> Image
                    </button>
                    <button onClick={handleSave} disabled={loading} className="w-full border border-primary text-primary font-label-md text-label-md py-3 rounded-full hover:bg-surface-container-low transition-colors flex justify-center items-center gap-2">
                      <span className="material-symbols-outlined">bookmark</span> Save
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </section>


      </main>
    </div>
  );
}
