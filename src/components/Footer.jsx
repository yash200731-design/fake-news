import React from 'react';
import { ShieldCheck } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-dark-primary border-t border-dark-border py-12 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          
          {/* Left branding */}
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-brand-green/10 flex items-center justify-center border border-brand-green/30">
              <ShieldCheck className="w-5 h-5 text-brand-green" />
            </div>
            <span className="font-display font-bold text-base tracking-tight text-text-primary">
              Veri<span className="text-brand-green">Truth</span> <span className="text-[10px] text-text-muted font-mono">v1.0.0</span>
            </span>
          </div>

          {/* Center Links (Mock Info) */}
          <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-2 text-xs text-text-secondary">
            <a href="#analyze" className="hover:text-brand-green transition-colors">Analyzer</a>
            <a href="#features" className="hover:text-brand-green transition-colors">Capabilities</a>
            <a href="#about" className="hover:text-brand-green transition-colors">NLP Research</a>
            <a href="#faq" className="hover:text-brand-green transition-colors">FAQ</a>
            <a href="#contact" className="hover:text-brand-green transition-colors">Contact</a>
          </div>

          {/* Right Socials */}
          <div className="flex items-center space-x-4">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="w-9 h-9 rounded-xl bg-dark-secondary/45 flex items-center justify-center border border-dark-border hover:border-brand-green text-text-secondary hover:text-text-primary transition-all cursor-pointer"
              title="GitHub Repository"
            >
              <svg className="w-4.5 h-4.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
                <path d="M9 18c-4.51 2-5-2-7-2" />
              </svg>
            </a>
            <a
              href="https://linkedin.com"
              target="_blank"
              rel="noopener noreferrer"
              className="w-9 h-9 rounded-xl bg-dark-secondary/45 flex items-center justify-center border border-dark-border hover:border-brand-green text-text-secondary hover:text-text-primary transition-all cursor-pointer"
              title="LinkedIn Profile"
            >
              <svg className="w-4.5 h-4.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
                <rect width="4" h="12" x="2" y="9" />
                <circle cx="4" cy="4" r="2" />
              </svg>
            </a>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="mt-8 pt-8 border-t border-dark-border/20 flex flex-col sm:flex-row items-center justify-between text-[11px] text-text-muted gap-4">
          <p>© {new Date().getFullYear()} VeriTruth AI. All rights reserved. Open-source under MIT License.</p>
          <div className="flex space-x-4">
            <span className="cursor-default hover:text-brand-green transition-colors">Privacy Policy</span>
            <span className="cursor-default hover:text-brand-green transition-colors">Terms of Service</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
