import React from 'react';
import Navbar from '../components/Navbar';

export default function Profile() {
  return (
    <div className="bg-background text-on-background min-h-screen flex flex-col">
      <Navbar />
      
      {/* Main Content */}
      <main className="flex-grow w-full max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-12">
        {/* Profile Header */}
        <section className="mb-16 flex flex-col md:flex-row items-start md:items-center gap-8">
          <div className="w-24 h-24 md:w-32 md:h-32 rounded-full overflow-hidden shrink-0 border border-outline-variant">
            <img className="w-full h-full object-cover" alt="Profile" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBP4yKyF0jU-VHjFzlpWSTiqnzwgfMOaFnINQuUc5JpQXIUaH3kjkcA2mFMMwL75rMpVjkA4IrOuE3FyjxhWVm5uPjNSQNPX0Mrf7MxeWjAOtuSGKkEJp3FGy8QgBk5QQiwzZYsoJ0d5sIobBFmvtjZ4hHUhQjng9y4ZLVrZCJlc3SI3dUhwmKCqUdY9laMJFax2Elfac95AMkLHqtqmjOh4H9IbNVPmC2-5jU-SxJ5ftpm_2mCaVU"/>
          </div>
          <div className="flex-grow">
            <h1 className="font-display-lg text-display-lg text-primary mb-2">Eleanor Vance</h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant mb-4">eleanor.vance@example.com</p>
            <button className="bg-primary text-on-primary font-label-md text-label-md px-6 py-2 rounded-full hover:bg-on-surface-variant transition-colors">Edit Profile</button>
          </div>
        </section>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
          {/* Left Column: Settings & Preferences */}
          <div className="col-span-1 md:col-span-4 space-y-8">
            {/* Account Settings */}
            <section>
              <h2 className="font-headline-md text-headline-md text-primary mb-6 border-b border-outline-variant pb-2">Account Settings</h2>
              <ul className="space-y-4 font-body-md text-body-md text-on-surface">
                <li className="flex justify-between items-center py-2 border-b border-surface-container-highest cursor-pointer hover:text-primary transition-colors">
                  <span>Password & Security</span>
                  <span className="material-symbols-outlined text-outline">chevron_right</span>
                </li>
                <li className="flex justify-between items-center py-2 border-b border-surface-container-highest cursor-pointer hover:text-primary transition-colors">
                  <span>Notifications</span>
                  <span className="material-symbols-outlined text-outline">chevron_right</span>
                </li>
                <li className="flex justify-between items-center py-2 border-b border-surface-container-highest cursor-pointer hover:text-primary transition-colors">
                  <span>Billing & Subscription</span>
                  <span className="material-symbols-outlined text-outline">chevron_right</span>
                </li>
                <li className="flex justify-between items-center py-2 border-b border-surface-container-highest cursor-pointer hover:text-primary transition-colors">
                  <span>Data Privacy</span>
                  <span className="material-symbols-outlined text-outline">chevron_right</span>
                </li>
              </ul>
            </section>
          </div>

          {/* Right Column: Connections & Stats */}
          <div className="col-span-1 md:col-span-8 space-y-12">
            {/* Platform Connections */}
            <section>
              <h2 className="font-headline-md text-headline-md text-primary mb-6 border-b border-outline-variant pb-2">Connected Platforms</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Connection Card */}
                <div className="border border-outline-variant p-6 flex items-center justify-between bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
                  <div className="flex items-center gap-4">
                    <span className="material-symbols-outlined text-primary text-[32px]">photo_camera</span>
                    <div>
                      <h3 className="font-label-md text-label-md text-primary">Instagram</h3>
                      <p className="font-label-sm text-label-sm text-on-surface-variant">@eleanor_v</p>
                    </div>
                  </div>
                  <span className="font-label-sm text-label-sm text-surface-tint border border-surface-tint px-3 py-1 rounded-full">Connected</span>
                </div>
                {/* Connection Card */}
                <div className="border border-outline-variant p-6 flex items-center justify-between bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
                  <div className="flex items-center gap-4">
                    <span className="material-symbols-outlined text-primary text-[32px]">work</span>
                    <div>
                      <h3 className="font-label-md text-label-md text-primary">LinkedIn</h3>
                      <p className="font-label-sm text-label-sm text-on-surface-variant">/in/eleanorvance</p>
                    </div>
                  </div>
                  <span className="font-label-sm text-label-sm text-surface-tint border border-surface-tint px-3 py-1 rounded-full">Connected</span>
                </div>
                {/* Connection Card */}
                <div className="border border-outline-variant p-6 flex items-center justify-between bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
                  <div className="flex items-center gap-4">
                    <span className="material-symbols-outlined text-primary text-[32px]">alternate_email</span>
                    <div>
                      <h3 className="font-label-md text-label-md text-primary">X</h3>
                      <p className="font-label-sm text-label-sm text-on-surface-variant">@eleanorv_writes</p>
                    </div>
                  </div>
                  <button className="font-label-sm text-label-sm text-primary hover:underline">Connect</button>
                </div>
                {/* Connection Card */}
                <div className="border border-outline-variant p-6 flex items-center justify-between bg-surface-container-lowest hover:bg-surface-container-low transition-colors">
                  <div className="flex items-center gap-4">
                    <span className="material-symbols-outlined text-primary text-[32px]">public</span>
                    <div>
                      <h3 className="font-label-md text-label-md text-primary">Facebook</h3>
                      <p className="font-label-sm text-label-sm text-on-surface-variant">Not connected</p>
                    </div>
                  </div>
                  <button className="font-label-sm text-label-sm text-primary hover:underline">Connect</button>
                </div>
              </div>
            </section>

            {/* Usage Statistics (Bento Style) */}
            <section>
              <h2 className="font-headline-md text-headline-md text-primary mb-6 border-b border-outline-variant pb-2">Usage Insights</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="col-span-2 md:col-span-2 bg-surface-container p-6 border border-outline-variant">
                  <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest mb-2">Generations this Month</p>
                  <div className="flex items-baseline gap-2">
                    <span className="font-display-lg text-display-lg text-primary">1,248</span>
                    <span className="font-label-sm text-label-sm text-surface-tint">/ 2,000</span>
                  </div>
                  <div className="w-full h-1 bg-outline-variant mt-4">
                    <div className="h-full bg-surface-tint w-3/5"></div>
                  </div>
                </div>
                <div className="col-span-1 bg-surface-container p-6 border border-outline-variant flex flex-col justify-between">
                  <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest mb-2">Saved Drafts</p>
                  <span className="font-headline-md text-headline-md text-primary">42</span>
                </div>
                <div className="col-span-1 bg-surface-container p-6 border border-outline-variant flex flex-col justify-between">
                  <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest mb-2">Active Campaigns</p>
                  <span className="font-headline-md text-headline-md text-primary">3</span>
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-surface w-full py-8 mt-auto border-t border-outline-variant">
        <div className="flex flex-col md:flex-row justify-between items-center px-margin-desktop max-w-container-max mx-auto gap-4">
          <div className="font-label-md text-label-md font-bold text-primary">
            © 2024 Social Generator. Editorial Precision by Design.
          </div>
          <nav className="flex gap-6 font-label-sm text-label-sm">
            <a className="text-on-surface-variant hover:text-primary transition-colors" href="#">Privacy</a>
            <a className="text-on-surface-variant hover:text-primary transition-colors" href="#">Terms</a>
            <a className="text-on-surface-variant hover:text-primary transition-colors" href="#">Support</a>
          </nav>
        </div>
      </footer>
    </div>
  );
}
