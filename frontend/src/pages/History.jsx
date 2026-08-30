import React from 'react';
import Navbar from '../components/Navbar';

export default function History() {
  return (
    <div className="bg-surface-container-low min-h-screen flex flex-col font-body-md text-on-surface">
      <Navbar />
      
      <main className="flex-grow w-full max-w-[900px] mx-auto px-margin-mobile md:px-0 py-12">
        <div className="bg-surface border border-outline-variant rounded-lg">
          {/* Header Section */}
          <div className="p-6 border-b border-outline-variant flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <h1 className="font-headline-lg text-headline-lg text-primary">Past Generations</h1>
            <div className="flex items-center gap-4 w-full md:w-auto">
              <div className="relative w-full md:w-64">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline-variant text-sm">search</span>
                <input className="w-full pl-10 pr-4 py-2 border border-outline-variant rounded bg-surface focus:outline-none focus:border-primary focus:ring-0 font-body-md text-body-md placeholder-outline" placeholder="Search past posts..." type="text"/>
              </div>
              <select className="border border-outline-variant rounded px-4 py-2 bg-surface focus:outline-none focus:border-primary font-body-md text-body-md">
                <option>All Platforms</option>
                <option>Twitter</option>
                <option>LinkedIn</option>
                <option>Instagram</option>
              </select>
            </div>
          </div>
          
          {/* List Section */}
          <div className="flex flex-col">
            {/* Row 1 */}
            <div className="flex flex-col md:flex-row items-start md:items-center p-6 border-b border-outline-variant hover:bg-surface-container-lowest transition-colors gap-6">
              <img alt="Thumbnail" className="w-24 h-24 object-cover rounded border border-outline-variant shrink-0" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDdyYCA-rSmxMs85eHBJxMCC_Yq_doFtyney_-1ZaI2dKaNYOEbtG8AnuSns3zbgRzJH7b5e-z6tPft-jSB1xrl8fDlo4rxxwKq-L62mHPxweyCuZSPGCksCIMNLtNidBkeKFwp6mxTcP6xyG4BxIbtI4N6tSX12C-xLuMCl4V5AkNwJ_5kM1YmSu8Z289XW2eKyJpKXTIgBbYabvEZj2LA10YwWSsS7A1froJmnP-S6UI98HiPi6s"/>
              <div className="flex-grow min-w-0">
                <div className="flex items-center gap-3 mb-2">
                  <span className="bg-primary-container text-on-primary-container font-label-sm text-label-sm px-2 py-0.5 rounded-full">LinkedIn</span>
                  <span className="text-outline font-label-sm text-label-sm">2 hours ago</span>
                  <div className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-secondary"></span>
                    <span className="text-outline font-label-sm text-label-sm">Published</span>
                  </div>
                </div>
                <p className="font-body-md text-body-md text-on-surface truncate">Excited to announce our new editorial design system, bringing a sense of calm and focus back to digital interfaces.</p>
              </div>
              <a className="font-label-md text-label-md text-secondary hover:text-primary underline shrink-0 mt-4 md:mt-0" href="#">Restore</a>
            </div>

            {/* Row 2 */}
            <div className="flex flex-col md:flex-row items-start md:items-center p-6 border-b border-outline-variant hover:bg-surface-container-lowest transition-colors gap-6">
              <img alt="Thumbnail" className="w-24 h-24 object-cover rounded border border-outline-variant shrink-0" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBsekolSqPPbqQ5Dl0nOnEilvGnhPa22sfNTsLCJYPOusUuPBKQ3o-razXoZhNWcCJEvqIRPDr-LDkEHdb8bBJ3Df6mtZquFvADm8hjwFsV5zhbTSnHk_gtNsUXOD_rhaF7sLJ6xkCeDE_tnVAnNdxZ7g9mgZapVDwiqQxcgzTGHERin5xUZGsMHO5sVfRWZYAuJoM8WQ7ZMnUEvuOgc10vVX82foVtDyYts0ab-gNFwZSFqXt3FB4"/>
              <div className="flex-grow min-w-0">
                <div className="flex items-center gap-3 mb-2">
                  <span className="bg-surface-variant text-on-surface-variant font-label-sm text-label-sm px-2 py-0.5 rounded-full">Twitter</span>
                  <span className="text-outline font-label-sm text-label-sm">Yesterday</span>
                  <div className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-error"></span>
                    <span className="text-outline font-label-sm text-label-sm">Draft</span>
                  </div>
                </div>
                <p className="font-body-md text-body-md text-on-surface truncate">Thread: 5 reasons why whitespace is your most powerful design tool. 🧵 #DesignThinking</p>
              </div>
              <a className="font-label-md text-label-md text-secondary hover:text-primary underline shrink-0 mt-4 md:mt-0" href="#">Restore</a>
            </div>

            {/* Row 3 */}
            <div className="flex flex-col md:flex-row items-start md:items-center p-6 hover:bg-surface-container-lowest transition-colors gap-6">
              <img alt="Thumbnail" className="w-24 h-24 object-cover rounded border border-outline-variant shrink-0" src="https://lh3.googleusercontent.com/aida-public/AB6AXuChlroOEbVFuAkLRoNHphlijY2lUYUC8lvr_Qnh3rrbhj1LHPvH8gGjg5HDAuY2hU4hVmvzSf_fkWMtKbhVQM6wDoZ9pax89uErL3Gagz7bEqiPXLaXPlV7n2qUxJa6EkdYxPeNHZ4W5YZiaUanLZ_yHan54jatfBAUIbbvynJHWXynFGZh5fBmGUvi6K3hKHbqUBwno1EmrRut1JhurF2MR-Xjo6RHl5akCsOzWbArX2u2RRYO8Qs"/>
              <div className="flex-grow min-w-0">
                <div className="flex items-center gap-3 mb-2">
                  <span className="bg-primary-container text-on-primary-container font-label-sm text-label-sm px-2 py-0.5 rounded-full">Instagram</span>
                  <span className="text-outline font-label-sm text-label-sm">Oct 12, 2023</span>
                  <div className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-secondary"></span>
                    <span className="text-outline font-label-sm text-label-sm">Published</span>
                  </div>
                </div>
                <p className="font-body-md text-body-md text-on-surface truncate">Finding beauty in structure. A sneak peek at our upcoming grid system documentation.</p>
              </div>
              <a className="font-label-md text-label-md text-secondary hover:text-primary underline shrink-0 mt-4 md:mt-0" href="#">Restore</a>
            </div>
          </div>
        </div>
      </main>
      
      {/* Footer */}
      <footer className="bg-surface w-full py-8 mt-auto border-t border-outline-variant">
        <div className="flex flex-col md:flex-row justify-between items-center px-margin-desktop max-w-container-max mx-auto gap-4">
          <div className="font-label-md text-label-md font-bold text-primary">
            © 2024 Social Generator. Editorial Precision by Design.
          </div>
          <div className="flex gap-4">
            <a className="font-label-sm text-label-sm text-on-surface-variant hover:text-primary transition-colors" href="#">Privacy</a>
            <a className="font-label-sm text-label-sm text-on-surface-variant hover:text-primary transition-colors" href="#">Terms</a>
            <a className="font-label-sm text-label-sm text-on-surface-variant hover:text-primary transition-colors" href="#">Support</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
