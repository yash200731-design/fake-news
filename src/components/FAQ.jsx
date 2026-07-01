import React, { useState } from 'react';
import { Plus, Minus, HelpCircle } from 'lucide-react';

export default function FAQ() {
  const [activeIndex, setActiveIndex] = useState(null);

  const faqs = [
    {
      q: 'How does the AI model determine if news is fake?',
      a: 'The classifier evaluates structural elements of the article, such as vocabulary distributions, passive vs. active verbs, clickbait language, capitalization rates, and exclamation marks. Rather than verifying facts directly, it flags patterns associated with misinformation narratives.',
    },
    {
      q: 'How do I integrate my own FastAPI backend?',
      a: 'The frontend is pre-wired to invoke a REST API. You can configure your FastAPI service to listen on http://localhost:8000/api/predict and accept a POST request with the body {"text": "..."}. Set the environment variable VITE_API_URL to point to your deployed backend.',
    },
    {
      q: 'What does the confidence score mean?',
      a: 'The confidence score represents the statistical probability assigned by the final sigmoid layer of our classification model. A 92% confidence rating for "Fake" means the model calculates a 92% probability that the stylistic pattern belongs to fake news patterns.',
    },
    {
      q: 'Is my data stored on your servers?',
      a: 'No. All analyzed text is passed to the prediction service in memory and is not stored. Your prediction history is saved entirely client-side in your browser using local storage.',
    },
    {
      q: 'Can I analyze social media posts or shorter text?',
      a: 'Yes, but for optimal results we recommend pasting articles of at least 150 words. NLP models require sufficient text length to detect syntactical signatures and provide highly accurate classifications.',
    }
  ];

  const handleToggle = (index) => {
    setActiveIndex(activeIndex === index ? null : index);
  };

  return (
    <section id="faq" className="py-20 relative overflow-hidden">
      <div className="absolute bottom-10 left-10 w-[300px] h-[300px] rounded-full bg-brand-green/5 blur-[100px] pointer-events-none" />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Title */}
        <div className="text-center mb-14 space-y-3">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-green/10 border border-brand-green/20 text-brand-green text-xs font-semibold uppercase tracking-wider">
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Got Questions?</span>
          </div>
          <h2 className="font-display font-extrabold text-3xl text-white">
            Frequently Asked Questions
          </h2>
          <p className="text-slate-400 text-sm max-w-md mx-auto">
            Learn more about NLP classifiers, technical integrations, and data handling.
          </p>
        </div>

        {/* Accordions */}
        <div className="space-y-4">
          {faqs.map((faq, idx) => {
            const isOpen = activeIndex === idx;
            return (
              <div 
                key={idx}
                className={`rounded-2xl border transition-all duration-300 ${
                  isOpen 
                    ? 'bg-slate-900/80 border-brand-green/35 shadow-md shadow-brand-green/5' 
                    : 'bg-dark-card/30 border-dark-border/40 hover:border-slate-700'
                }`}
              >
                {/* Accordion Toggle */}
                <button
                  onClick={() => handleToggle(idx)}
                  className="w-full flex items-center justify-between p-5 text-left text-white font-display font-semibold text-sm sm:text-base select-none cursor-pointer"
                >
                  <span>{faq.q}</span>
                  <span className={`w-6 h-6 rounded-lg bg-slate-800 flex items-center justify-center border border-slate-700/60 transition-transform duration-300 ${
                    isOpen ? 'rotate-180 border-brand-green/30' : ''
                  }`}>
                    {isOpen ? (
                      <Minus className="w-3.5 h-3.5 text-brand-green" />
                    ) : (
                      <Plus className="w-3.5 h-3.5 text-slate-400" />
                    )}
                  </span>
                </button>

                {/* Accordion Content */}
                <div className={`overflow-hidden transition-all duration-300 ease-in-out ${
                  isOpen ? 'max-h-[300px] opacity-100' : 'max-h-0 opacity-0'
                }`}>
                  <p className="px-5 pb-5 text-slate-400 text-xs sm:text-sm leading-relaxed border-t border-dark-border/10 pt-3">
                    {faq.a}
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
