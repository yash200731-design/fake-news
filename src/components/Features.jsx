import React from 'react';
import { Cpu, ShieldCheck, Zap, Lock, Globe, MessageSquareWarning } from 'lucide-react';

export default function Features() {
  const features = [
    {
      icon: Cpu,
      title: 'Neural Classification',
      desc: 'Powered by state-of-the-art NLP models that inspect syntactic and semantic layouts of news copy.',
    },
    {
      icon: ShieldCheck,
      title: 'High Integrity',
      desc: 'Our models are trained on curated datasets (including LIAR, ISOT) to minimize false positives.',
    },
    {
      icon: Zap,
      title: 'Sub-Second Speeds',
      desc: 'Get analytical outputs in under 1.5 seconds, giving you quick and actionable integrity data.',
    },
    {
      icon: Lock,
      title: 'Privacy Safeguards',
      desc: 'Your history is kept locally on your browser using localStorage. We do not track or sell your queries.',
    },
    {
      icon: Globe,
      title: 'API Integrations',
      desc: 'Ready to hook into a FastAPI production endpoint. Easily scale from single users to enterprise web crawlers.',
    },
    {
      icon: MessageSquareWarning,
      title: 'Clickbait Flagging',
      desc: 'Scans text for highly emotional exclamation patterns, uppercase spam, and misleading hook phrases.',
    },
  ];

  return (
    <section id="features" className="py-20 relative overflow-hidden">
      {/* Decorative Blur Backgrounds */}
      <div className="absolute bottom-10 right-1/4 w-[350px] h-[350px] rounded-full bg-brand-green/5 blur-[120px] pointer-events-none" />
      <div className="absolute top-10 left-10 w-[300px] h-[300px] rounded-full bg-brand-blue/5 blur-[100px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Title Block */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <span className="text-xs font-semibold text-brand-green uppercase tracking-widest bg-brand-green/10 border border-brand-green/20 px-3.5 py-1 rounded-full animate-pulse">
            Core Capabilities
          </span>
          <h2 className="font-display font-extrabold text-3xl sm:text-4xl text-text-primary">
            Engineered to Expose Deception
          </h2>
          <p className="text-text-secondary font-sans max-w-xl mx-auto text-sm sm:text-base leading-relaxed">
            VeriTruth AI analyzes linguistic signatures to flag narratives that lack evidence, use sensational formatting, or present fake claims.
          </p>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="glass-panel glass-panel-hover rounded-2xl p-6 border border-white/5 flex flex-col justify-between"
              >
                <div className="space-y-4">
                  {/* Icon Wrapper */}
                  <div className="w-12 h-12 rounded-xl bg-brand-green/10 flex items-center justify-center border border-brand-green/25">
                    <Icon className="w-6 h-6 text-brand-green" />
                  </div>
                  <h3 className="font-display font-bold text-lg text-text-primary">
                    {feature.title}
                  </h3>
                  <p className="text-text-secondary text-sm leading-relaxed">
                    {feature.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
