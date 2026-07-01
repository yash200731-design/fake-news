import React from 'react';
import { Sparkles, Activity, ShieldAlert, FileText } from 'lucide-react';

export default function Hero() {
  return (
    <section className="relative pt-32 pb-20 md:pt-40 md:pb-28 overflow-hidden">
      {/* Background Decorative Gradients */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full bg-brand-green/5 blur-[120px] pointer-events-none" />
      <div className="absolute top-1/3 left-1/4 w-[300px] h-[300px] rounded-full bg-brand-blue/5 blur-[100px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Hero Left Content */}
          <div className="lg:col-span-7 text-center lg:text-left space-y-6">
            {/* Tag Badge */}
            <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-brand-green/10 border border-brand-green/20 text-brand-green text-xs font-semibold tracking-wider uppercase animate-pulse mx-auto lg:mx-0">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Next-Gen Sentiment & Truth Analysis</span>
            </div>

            {/* Main Title */}
            <h1 className="font-display font-extrabold text-4xl sm:text-5xl lg:text-6xl tracking-tight text-white leading-tight">
              AI Fake News <br className="hidden sm:inline" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-green-light via-brand-green to-emerald-400">
                Detection Engine
              </span>
            </h1>

            {/* Description */}
            <p className="text-slate-300 text-base sm:text-lg max-w-xl mx-auto lg:mx-0 leading-relaxed font-sans">
              Safeguard your information feed with our advanced machine learning classifier. Analyze articles, detect sensationalism, identify deep-fake narratives, and receive accurate real-time integrity ratings in seconds.
            </p>

            {/* Call to Actions */}
            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-4">
              <a
                href="#analyze"
                className="w-full sm:w-auto px-8 py-4 rounded-xl bg-brand-green hover:bg-brand-green-dark text-dark-primary font-bold text-base transition-all duration-300 shadow-lg shadow-brand-green/20 hover:shadow-brand-green/40 hover:translate-y-[-2px]"
              >
                Analyze Article
              </a>
              <a
                href="#about"
                className="w-full sm:w-auto px-8 py-4 rounded-xl bg-dark-card/50 hover:bg-dark-card border border-dark-border text-slate-200 hover:text-white font-semibold text-base transition-all duration-300 backdrop-blur-sm"
              >
                Learn Methodology
              </a>
            </div>

            {/* Trust Stats / Features Row */}
            <div className="grid grid-cols-3 gap-6 pt-8 border-t border-dark-border/40 max-w-md mx-auto lg:mx-0">
              <div>
                <p className="font-display font-bold text-2xl text-white">98.4%</p>
                <p className="text-xs text-slate-400">Model Accuracy</p>
              </div>
              <div>
                <p className="font-display font-bold text-2xl text-white">&lt; 1.5s</p>
                <p className="text-xs text-slate-400">Response Time</p>
              </div>
              <div>
                <p className="font-display font-bold text-2xl text-white">10M+</p>
                <p className="text-xs text-slate-400">Articles Checked</p>
              </div>
            </div>
          </div>

          {/* Hero Right Visual */}
          <div className="lg:col-span-5 flex justify-center items-center">
            <div className="relative w-full max-w-[420px] aspect-square rounded-3xl glass-panel glow-green p-6 border border-white/10 flex flex-col justify-between overflow-hidden animate-float">
              {/* Decorative nodes */}
              <div className="absolute top-0 right-0 w-24 h-24 bg-brand-green/10 rounded-full blur-xl pointer-events-none" />
              <div className="absolute -bottom-8 -left-8 w-32 h-32 bg-brand-blue/10 rounded-full blur-2xl pointer-events-none" />

              {/* Card Header */}
              <div className="flex items-center justify-between pb-4 border-b border-dark-border/40 relative z-10">
                <div className="flex items-center space-x-2">
                  <Activity className="w-5 h-5 text-brand-green animate-pulse" />
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">System Monitor</span>
                </div>
                <span className="w-2.5 h-2.5 rounded-full bg-brand-green animate-ping" />
              </div>

              {/* Card Content Simulating Classifier */}
              <div className="space-y-4 my-6 flex-grow flex flex-col justify-center relative z-10">
                {/* Floating Box 1 */}
                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-700/50 flex items-center space-x-3 transform -rotate-1 hover:rotate-0 transition-transform">
                  <FileText className="w-5 h-5 text-brand-blue flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-slate-400 truncate">Pasted News Text Input</p>
                    <p className="text-xs font-semibold text-white truncate font-mono">"Breaking: Miracle vaccine cured..."</p>
                  </div>
                </div>

                {/* Processing Indicator */}
                <div className="flex items-center justify-center py-2">
                  <div className="flex space-x-1.5">
                    <span className="w-2 h-2 rounded-full bg-brand-green animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 rounded-full bg-brand-green animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 rounded-full bg-brand-green animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>

                {/* Floating Box 2 */}
                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-brand-green/30 flex items-center space-x-3 transform rotate-1 hover:rotate-0 transition-transform shadow-md shadow-brand-green/5">
                  <ShieldAlert className="w-5 h-5 text-brand-green flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-slate-400">Classification Result</p>
                    <p className="text-sm font-bold text-brand-green flex items-center">
                      92.4% Probability of Sensationalism
                    </p>
                  </div>
                </div>
              </div>

              {/* Card Footer */}
              <div className="pt-4 border-t border-dark-border/40 flex items-center justify-between text-[11px] text-slate-400 relative z-10">
                <span>Model v4.1.2-Stable</span>
                <span>CORS SSL Encrypted</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
