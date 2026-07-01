import React, { useState } from 'react';
import { Send, CheckCircle, Mail, MessageSquare, User } from 'lucide-react';

export default function Contact() {
  const [formData, setFormData] = useState({ name: '', email: '', message: '' });
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.name && formData.email && formData.message) {
      setLoading(true);
      // Simulate form submission delay
      setTimeout(() => {
        setLoading(false);
        setSubmitted(true);
        setFormData({ name: '', email: '', message: '' });
        // Reset success state after 5 seconds
        setTimeout(() => setSubmitted(false), 5000);
      }, 1000);
    }
  };

  return (
    <section id="contact" className="py-20 relative overflow-hidden bg-dark-secondary/20 border-t border-dark-border/40">
      <div className="absolute top-1/3 right-10 w-[250px] h-[250px] rounded-full bg-brand-blue/5 blur-[120px] pointer-events-none" />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Title block */}
        <div className="text-center mb-14 space-y-3">
          <span className="text-xs font-semibold text-brand-green uppercase tracking-widest bg-brand-green/10 border border-brand-green/20 px-3.5 py-1 rounded-full">
            Get In Touch
          </span>
          <h2 className="font-display font-extrabold text-3xl text-white">
            Contact Our Research Team
          </h2>
          <p className="text-slate-400 text-sm max-w-sm mx-auto">
            Have questions about dataset training, false-positive reporting, or integrations? Drop us a line.
          </p>
        </div>

        {/* Contact Form Container */}
        <div className="glass-panel rounded-2xl p-6 sm:p-10 border border-white/5 glow-green max-w-2xl mx-auto">
          {submitted ? (
            <div className="text-center py-8 space-y-4 animate-fadeIn">
              <div className="w-16 h-16 rounded-full bg-brand-green/15 flex items-center justify-center border border-brand-green/30 mx-auto">
                <CheckCircle className="w-8 h-8 text-brand-green" />
              </div>
              <h3 className="font-display font-bold text-xl text-white">Message Transmitted!</h3>
              <p className="text-slate-400 text-sm max-w-xs mx-auto leading-relaxed">
                Thank you for contacting VeriTruth AI. A member of our NLP engineering team will review your inquiry.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                
                {/* Name */}
                <div className="space-y-2">
                  <label htmlFor="name" className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                    <User className="w-3.5 h-3.5 text-brand-green" /> Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    placeholder="Jane Doe"
                    disabled={loading}
                    className="w-full bg-slate-950/40 text-slate-100 placeholder-slate-600 border border-slate-800 rounded-xl px-4 py-3 focus:outline-none focus:border-brand-green/60 text-sm transition-colors"
                  />
                </div>

                {/* Email */}
                <div className="space-y-2">
                  <label htmlFor="email" className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                    <Mail className="w-3.5 h-3.5 text-brand-green" /> Email
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    placeholder="jane@example.com"
                    disabled={loading}
                    className="w-full bg-slate-950/40 text-slate-100 placeholder-slate-600 border border-slate-800 rounded-xl px-4 py-3 focus:outline-none focus:border-brand-green/60 text-sm transition-colors"
                  />
                </div>

              </div>

              {/* Message */}
              <div className="space-y-2">
                <label htmlFor="message" className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                  <MessageSquare className="w-3.5 h-3.5 text-brand-green" /> Message
                </label>
                <textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  required
                  rows="5"
                  placeholder="Tell us about your query..."
                  disabled={loading}
                  className="w-full bg-slate-950/40 text-slate-100 placeholder-slate-600 border border-slate-800 rounded-xl p-4 focus:outline-none focus:border-brand-green/60 resize-none text-sm transition-colors"
                />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className={`w-full py-4 px-6 rounded-xl font-bold text-sm tracking-wider uppercase transition-all duration-300 flex items-center justify-center gap-2 cursor-pointer ${
                  loading 
                    ? 'bg-brand-green/20 text-brand-green border border-brand-green/30 cursor-not-allowed'
                    : 'bg-brand-green hover:bg-brand-green-dark text-dark-primary shadow-lg shadow-brand-green/10 hover:shadow-brand-green/20 hover:translate-y-[-1px]'
                }`}
              >
                {loading ? 'Transmitting...' : 'Send Message'}
                <Send className="w-4 h-4" />
              </button>
            </form>
          )}
        </div>

      </div>
    </section>
  );
}
