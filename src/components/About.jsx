import React from 'react';
import { Network, FileSearch, Layers, Sliders } from 'lucide-react';

export default function About() {
  const steps = [
    {
      step: '01',
      icon: FileSearch,
      title: 'Syntactic Parsing',
      desc: 'Removes stopwords, parses word stems, and processes vocabulary distributions to isolate claims.',
    },
    {
      step: '02',
      icon: Sliders,
      title: 'Feature Vectorizing',
      desc: 'Translates clean article strings into numerical arrays (TF-IDF/Embeddings) representing context.',
    },
    {
      step: '03',
      icon: Network,
      title: 'Model Evaluation',
      desc: 'Feeds variables into classifiers (Passive Aggressive, LSTM, or BERT) to score linguistic truth.',
    },
    {
      step: '04',
      icon: Layers,
      title: 'Verdict Calibration',
      desc: 'Compares confidence thresholds and builds a final probability score (Real vs Fake % Output).',
    },
  ];

  return (
    <section id="about" className="py-20 relative overflow-hidden bg-dark-secondary/40 border-y border-dark-border/40">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-brand-blue/5 blur-[130px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          {/* Left Description Column */}
          <div className="lg:col-span-5 space-y-6 text-center lg:text-left">
            <span className="text-xs font-semibold text-brand-green uppercase tracking-widest bg-brand-green/10 border border-brand-green/20 px-3.5 py-1 rounded-full">
              Linguistic Methodology
            </span>
            <h2 className="font-display font-extrabold text-3xl sm:text-4xl text-text-primary leading-tight">
              Combating Deception with Deep Learning
            </h2>
            <p className="text-text-secondary text-sm sm:text-base leading-relaxed">
              VeriTruth AI was founded on the principle that disinformation spreads six times faster than the truth. By analyzing pattern weights in human text, our classifiers can identify sensational biases, missing references, and emotional manipulation.
            </p>
            <p className="text-text-muted text-sm leading-relaxed">
              We leverage Natural Language Processing (NLP) to inspect article syntax. Instead of verifying facts directly against database tables, we look at <em>how</em> a story is written, identifying stylistic fingerprints common to verified journalism versus clickbait campaigns.
            </p>
          </div>

          {/* Right Pipeline Steps Column */}
          <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-4">
            {steps.map((step, idx) => {
              const Icon = step.icon;
              return (
                <div 
                  key={idx}
                  className="p-5 rounded-2xl bg-dark-primary/30 border border-dark-border/40 hover:border-brand-green/30 transition-all duration-300 group flex items-start gap-4"
                >
                  <div className="w-10 h-10 rounded-xl bg-brand-green/5 border border-brand-green/15 flex items-center justify-center flex-shrink-0 group-hover:bg-brand-green/10 transition-colors">
                    <Icon className="w-5 h-5 text-brand-green" />
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center justify-between">
                      <h4 className="font-display font-bold text-sm text-text-primary group-hover:text-brand-green transition-colors">
                        {step.title}
                      </h4>
                      <span className="text-[10px] font-mono text-text-muted font-bold">
                        {step.step}
                      </span>
                    </div>
                    <p className="text-text-secondary text-xs leading-relaxed">
                      {step.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

        </div>
      </div>
    </section>
  );
}
