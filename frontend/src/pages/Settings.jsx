import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import { useAuth } from '../contexts/AuthContext';

export default function Settings() {
  const { currentUser } = useAuth();
  const [displayName, setDisplayName] = useState('');
  const [bio, setBio] = useState('');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    // TODO: persist profile to backend
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="bg-background text-on-background min-h-screen flex flex-col">
      <Navbar />
      
      <main className="flex-grow w-full max-w-[900px] mx-auto px-4 md:px-8 py-12">
        {/* Profile Header */}
        <section className="mb-12 flex flex-col md:flex-row items-start md:items-center gap-8">
          <div className="w-24 h-24 md:w-32 md:h-32 rounded-full overflow-hidden shrink-0 border border-outline-variant bg-surface-container-high flex items-center justify-center">
            {currentUser?.photoURL ? (
              <img className="w-full h-full object-cover" alt="Profile" src={currentUser.photoURL} />
            ) : (
              <span className="material-symbols-outlined text-[48px] text-on-surface-variant">person</span>
            )}
          </div>
          <div className="flex-grow">
            <h1 className="font-display-lg text-display-lg text-primary mb-2">
              {currentUser?.displayName || 'Your Name'}
            </h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant">
              {currentUser?.email || 'your@email.com'}
            </p>
          </div>
        </section>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
          {/* Left: Edit Profile */}
          <div className="col-span-1 md:col-span-6">
            <section className="bg-surface border border-outline-variant rounded-lg p-6 flex flex-col gap-6">
              <h2 className="font-headline-md text-headline-md text-primary border-b border-outline-variant pb-2">Edit Profile</h2>
              
              <div className="flex flex-col gap-2">
                <label className="font-label-md text-label-md text-primary">Display Name</label>
                <input
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  className="w-full bg-surface border border-outline-variant rounded p-3 font-body-md text-body-md text-on-surface focus:border-primary focus:ring-0 transition-colors"
                  placeholder="Enter your display name"
                  type="text"
                />
              </div>

              <div className="flex flex-col gap-2">
                <label className="font-label-md text-label-md text-primary">Bio</label>
                <textarea
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  className="w-full bg-surface border border-outline-variant rounded p-3 font-body-md text-body-md text-on-surface focus:border-primary focus:ring-0 transition-colors resize-none"
                  placeholder="Tell us about yourself"
                  rows="3"
                />
              </div>

              <button
                onClick={handleSave}
                className="w-fit bg-primary-container text-on-primary font-label-md text-label-md px-6 py-2 rounded-full hover:opacity-90 transition-opacity"
              >
                {saved ? 'Saved!' : 'Save Changes'}
              </button>
            </section>
          </div>

          {/* Right: Connected Platforms */}
          <div className="col-span-1 md:col-span-6">
            <section className="bg-surface border border-outline-variant rounded-lg p-6 flex flex-col gap-6">
              <h2 className="font-headline-md text-headline-md text-primary border-b border-outline-variant pb-2">Connected Platforms</h2>
              
              <div className="flex flex-col gap-3">
                {[
                  { name: 'Instagram', icon: 'photo_camera' },
                  { name: 'LinkedIn', icon: 'work' },
                  { name: 'X', icon: 'alternate_email' },
                  { name: 'Facebook', icon: 'public' },
                ].map((p) => (
                  <div key={p.name} className="border border-outline-variant p-4 flex items-center justify-between bg-surface-container-lowest rounded hover:bg-surface-container-low transition-colors">
                    <div className="flex items-center gap-3">
                      <span className="material-symbols-outlined text-primary text-[24px]">{p.icon}</span>
                      <h3 className="font-label-md text-label-md text-primary">{p.name}</h3>
                    </div>
                    <button className="font-label-sm text-label-sm text-primary hover:underline">Connect</button>
                  </div>
                ))}
              </div>
            </section>
          </div>
        </div>
      </main>

      <footer className="bg-surface w-full py-8 mt-auto border-t border-outline-variant">
        <div className="flex justify-center px-8 max-w-[900px] mx-auto">
          <div className="font-label-md text-label-md font-bold text-primary">
            © 2024 Social Generator
          </div>
        </div>
      </footer>
    </div>
  );
}
