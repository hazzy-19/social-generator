import React, { useState } from 'react';
import Navbar from '../components/Navbar';

export default function Dashboard() {
  const [topic, setTopic] = useState('');
  const [platform, setPlatform] = useState('linkedin');
  const [loading, setLoading] = useState(false);
  
  const [caption, setCaption] = useState('');
  const [hashtags, setHashtags] = useState([]);
  const [imageUrl, setImageUrl] = useState('');
  
  const [generationId, setGenerationId] = useState(null);
  const [imageApproved, setImageApproved] = useState(false);
  const [captionApproved, setCaptionApproved] = useState(false);
  const [hashtagsApproved, setHashtagsApproved] = useState(false);

  const platforms = [
    { id: 'instagram', label: 'Instagram' },
    { id: 'linkedin', label: 'LinkedIn' },
    { id: 'x', label: 'X' },
    { id: 'facebook', label: 'Facebook' },
  ];

  const [error, setError] = useState('');

  const handleGenerate = async () => {
    if (!topic) return;
    setLoading(true);
    setError('');
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000); // 120s timeout

    try {
      const response = await fetch('http://127.0.0.1:8000/generations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_content: topic,
          platform: platform
        }),
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      const data = await response.json();
      
      if (response.ok) {
        setGenerationId(data.id);
        setCaption(data.caption);
        setHashtags(data.hashtags);
        setImageUrl(data.image_url);
        setImageApproved(data.image_approved);
        setCaptionApproved(data.caption_approved);
        setHashtagsApproved(data.hashtags_approved);
      } else {
        const errorMsg = Array.isArray(data.detail) ? data.detail[0].msg : data.detail;
        setError(errorMsg || 'Error generating content');
      }
    } catch (err) {
      clearTimeout(timeoutId);
      console.error(err);
      if (err.name === 'AbortError') {
        setError('Request timed out. Please try again.');
      } else {
        setError('Failed to connect to backend.');
      }
    } finally {
      setLoading(false);
    }
  }

  const handleReload = async (section) => {
    if (!generationId) return;
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`http://127.0.0.1:8000/generations/${generationId}/reload/${section}`, {
        method: 'POST'
      });
      const data = await response.json();
      if (response.ok) {
        setCaption(data.caption);
        setHashtags(data.hashtags);
        setImageUrl(data.image_url);
        setImageApproved(data.image_approved);
        setCaptionApproved(data.caption_approved);
        setHashtagsApproved(data.hashtags_approved);
      } else {
        setError(data.detail || `Error reloading ${section}`);
      }
    } catch (err) {
      setError('Failed to connect to backend.');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (section) => {
    if (!generationId) return;
    try {
      const response = await fetch(`http://127.0.0.1:8000/generations/${generationId}/approve/${section}`, {
        method: 'POST'
      });
      const data = await response.json();
      if (response.ok) {
        setImageApproved(data.image_approved);
        setCaptionApproved(data.caption_approved);
        setHashtagsApproved(data.hashtags_approved);
      } else {
        setError(data.detail || `Error approving ${section}`);
      }
    } catch (err) {
      setError('Failed to connect to backend.');
    }
  };

  const handleSave = async () => {
    if (!generationId) return;
    setLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/generations/${generationId}/save`, {
        method: 'POST'
      });
      if (response.ok) {
        alert('Post saved successfully!');
      } else {
        const data = await response.json();
        setError(data.detail || 'Error saving post');
      }
    } catch (err) {
      setError('Failed to connect to backend.');
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="min-h-screen text-on-background font-body-md py-12 px-4 md:px-8">
      <Navbar />
      
      <main className="max-w-[900px] mx-auto flex flex-col gap-8 mt-8">
        {/* SECTION 1: Generator Card */}
        <section className="bg-surface border border-outline-variant rounded p-8 flex flex-col gap-8">
          {/* Header */}
          <div className="flex flex-col gap-2">
            <h1 className="font-headline-lg text-headline-lg text-primary">Social Generator</h1>
            <p className="font-body-md text-body-md text-on-surface-variant">Paste or write source content, then generate a platform-ready post.</p>
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
            <button 
              onClick={handleGenerate} 
              disabled={loading}
              className="mt-2 w-fit bg-primary-container text-on-primary font-label-md text-label-md py-2 px-6 rounded hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              {loading ? 'Generating...' : 'Generate Post'}
            </button>
          </div>

          <hr className="border-t border-outline-variant w-full opacity-50" />

          {/* Platform Tabs */}
          <div className="flex gap-2 p-1 bg-surface-container-low rounded inline-flex w-fit">
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
                    <img alt="Generated" className="w-full h-full object-cover" src={imageUrl} />
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
                    <button onClick={() => handleReload('caption')} disabled={loading} className="font-label-sm text-label-sm text-primary underline hover:opacity-70 transition-opacity">✨ Regenerate</button>
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
                    {hashtags.map((tag, idx) => (
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
