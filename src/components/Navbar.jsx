import React, { useState, useEffect } from 'react';
import { ShieldCheck, Menu, X, ArrowRight, Sun, Moon } from 'lucide-react';

export default function Navbar({ theme, onToggleTheme }) {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Analyze', href: '#analyze' },
    { name: 'News Feed', href: '#news' },
    { name: 'Features', href: '#features' },
    { name: 'About', href: '#about' },
    { name: 'FAQ', href: '#faq' },
    { name: 'Contact', href: '#contact' },
  ];

  return (
    <nav className={`fixed top-0 left-0 w-full z-50 transition-all duration-300 ${
      scrolled 
        ? 'bg-dark-primary/80 backdrop-blur-md border-b border-dark-border py-4 shadow-lg' 
        : 'bg-transparent py-6'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <a href="#" className="flex items-center space-x-2 group">
            <div className="w-10 h-10 rounded-xl bg-brand-green/10 flex items-center justify-center border border-brand-green/30 group-hover:border-brand-green/60 transition-colors">
              <ShieldCheck className="w-6 h-6 text-brand-green" />
            </div>
            <span className="font-display font-bold text-xl tracking-tight text-text-primary">
              Veri<span className="text-brand-green">Truth</span> <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-brand-green/10 text-brand-green border border-brand-green/20">AI</span>
            </span>
          </a>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                className="text-text-secondary hover:text-brand-green font-medium text-sm transition-colors duration-200"
              >
                {link.name}
              </a>
            ))}
            
            {/* Theme Toggle Button */}
            <button
              onClick={onToggleTheme}
              className="p-2 rounded-lg bg-dark-secondary/40 text-text-secondary hover:text-text-primary border border-dark-border hover:border-brand-green transition-all duration-200 cursor-pointer flex items-center justify-center"
              aria-label="Toggle Theme"
              title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {theme === 'dark' ? (
                <Sun className="w-4 h-4 text-amber-400" />
              ) : (
                <Moon className="w-4 h-4 text-brand-blue" />
              )}
            </button>

            <a
              href="#analyze"
              className="inline-flex items-center justify-center px-4 py-2 rounded-lg bg-brand-green hover:bg-brand-green-dark text-dark-primary font-bold text-sm transition-all duration-200 shadow-md shadow-brand-green/20 hover:shadow-brand-green/30 hover:translate-y-[-1px]"
            >
              Start Analysis
              <ArrowRight className="w-4 h-4 ml-1.5" />
            </a>
          </div>

          {/* Mobile Menu Actions */}
          <div className="md:hidden flex items-center space-x-3">
            {/* Mobile Theme Toggle */}
            <button
              onClick={onToggleTheme}
              className="p-2 rounded-lg bg-dark-secondary/40 text-text-secondary border border-dark-border transition-all duration-200 cursor-pointer flex items-center justify-center"
              aria-label="Toggle Theme"
            >
              {theme === 'dark' ? (
                <Sun className="w-4.5 h-4.5 text-amber-400" />
              ) : (
                <Moon className="w-4.5 h-4.5 text-brand-blue" />
              )}
            </button>

            <button
              onClick={() => setIsOpen(!isOpen)}
              className="p-2 rounded-lg text-text-secondary hover:text-text-primary transition-colors"
              aria-label="Toggle menu"
            >
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      <div className={`md:hidden absolute top-full left-0 w-full bg-dark-secondary/95 border-b border-dark-border backdrop-blur-lg transition-all duration-300 ${
        isOpen ? 'opacity-100 translate-y-0 visible' : 'opacity-0 -translate-y-4 invisible pointer-events-none'
      }`}>
        <div className="px-4 pt-2 pb-6 space-y-3 sm:px-3">
          {navLinks.map((link) => (
            <a
              key={link.name}
              href={link.href}
              onClick={() => setIsOpen(false)}
              className="block px-3 py-2.5 rounded-lg text-text-secondary hover:text-brand-green hover:bg-slate-800/40 font-medium text-base transition-colors"
            >
              {link.name}
            </a>
          ))}
          <div className="pt-2 px-3">
            <a
              href="#analyze"
              onClick={() => setIsOpen(false)}
              className="w-full inline-flex items-center justify-center px-4 py-3 rounded-lg bg-brand-green hover:bg-brand-green-dark text-dark-primary font-bold text-base transition-all duration-200 shadow-md"
            >
              Start Analysis
              <ArrowRight className="w-4 h-4 ml-1.5" />
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
}
