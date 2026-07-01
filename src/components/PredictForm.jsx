import React, { useState, useEffect } from 'react';
import { Send, Sparkles, RefreshCw, FileText, CheckCircle2 } from 'lucide-react';

const SAMPLE_ARTICLES = [
  {
    label: 'Real Article Sample',
    category: 'Real',
    text: 'Researchers published a new peer-reviewed study on Wednesday in the Journal of Medicine detailing the impact of global trade shifts on local agricultural economies. According to the study, official reports from the agriculture department show a steady recovery in farm yields. A spokesperson stated that a press conference will be held next week to discuss long-term crop sustainability programs and water management reforms.',
  },
  {
    label: 'Fake Article Sample',
    category: 'Fake',
    text: 'SHOCKING TRUTH: A secret source has confirmed that alien spacecraft have landed in a hidden desert base. The government is keeping this quiet to hide the miracle technologies which could cure all illnesses instantly. Scientists are quiet because they are being controlled by the Illuminati who want to enforce 5G radiation microchips on the entire global population. Share this before it gets taken down by the media!',
  },
  {
    label: 'Sensational Sample',
    category: 'Mixed',
    text: 'The global economy is facing a critical turning point as tech stocks slide and energy prices hit record highs. Financial analysts warned that immediate regulatory reforms are needed to curb market volatility, although official spokesmen from the central bank urged calm during a senate hearing earlier today.',
  }
];

export default function PredictForm({ onPredict, loading, error, externalText }) {
  const [text, setText] = useState('');
  const maxChars = 8000;

  useEffect(() => {
    if (externalText) {
      setText(externalText);
    }
  }, [externalText]);

  const handleTextChange = (e) => {
    if (e.target.value.length <= maxChars) {
      setText(e.target.value);
    }
  };

  const handleAutofill = (sampleText) => {
    setText(sampleText);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim().length >= 15) {
      onPredict(text);
    }
  };

  const handleClear = () => {
    setText('');
  };

  return (
    <div className="w-full glass-panel rounded-2xl p-6 sm:p-8 border border-white/10 glow-green flex flex-col justify-between h-full">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title / Description */}
        <div className="flex items-center justify-between pb-3 border-b border-dark-border/40">
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-brand-green" />
            <h3 className="font-display font-bold text-lg text-white">Enter News Text</h3>
          </div>
          {text && (
            <button
              type="button"
              onClick={handleClear}
              className="text-xs font-semibold text-slate-400 hover:text-white transition-colors"
            >
              Clear Text
            </button>
          )}
        </div>

        {/* Text Area */}
        <div className="relative">
          <textarea
            value={text}
            onChange={handleTextChange}
            placeholder="Paste the full text of the news article here (minimum 15 characters)..."
            rows="8"
            disabled={loading}
            className="w-full bg-slate-950/50 text-slate-100 placeholder-slate-500 border border-slate-700/60 rounded-xl p-4 focus:outline-none focus:border-brand-green/75 focus:ring-1 focus:ring-brand-green/50 resize-y min-h-[160px] font-sans text-sm leading-relaxed transition-all disabled:opacity-55"
          />
          {loading && (
            <div className="absolute inset-0 bg-slate-950/40 backdrop-blur-[1px] rounded-xl flex items-center justify-center">
              <div className="flex items-center space-x-2 text-brand-green text-sm font-semibold">
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>AI is analyzing syntax structure...</span>
              </div>
            </div>
          )}
        </div>

        {/* Counter and Form Validation */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div>
            {error && (
              <span className="text-red-400 font-medium">
                ⚠️ {error}
              </span>
            )}
            {!error && text.trim().length > 0 && text.trim().length < 15 && (
              <span className="text-amber-400 font-medium">
                Add {15 - text.trim().length} more characters to analyze
              </span>
            )}
            {!error && text.trim().length >= 15 && (
              <span className="text-brand-green flex items-center gap-1 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" /> Ready for analysis
              </span>
            )}
          </div>
          <div className="text-slate-400 font-mono text-right">
            {text.length} / {maxChars} characters
          </div>
        </div>

        {/* Autofill / Samples Section */}
        <div className="space-y-2 pt-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest block">
            Try Sample Articles:
          </span>
          <div className="flex flex-wrap gap-2.5">
            {SAMPLE_ARTICLES.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleAutofill(sample.text)}
                disabled={loading}
                className="text-xs px-3 py-2 rounded-lg bg-dark-primary/60 hover:bg-slate-900 border border-dark-border/50 text-slate-300 hover:text-white transition-all duration-200 cursor-pointer disabled:opacity-50"
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>

        {/* Predict Action Button */}
        <button
          type="submit"
          disabled={loading || text.trim().length < 15}
          className={`w-full py-4 px-6 rounded-xl font-bold text-sm tracking-wider uppercase transition-all duration-300 flex items-center justify-center gap-2 cursor-pointer shadow-md ${
            loading
              ? 'bg-brand-green/20 text-brand-green border border-brand-green/30 cursor-not-allowed'
              : text.trim().length < 15
              ? 'bg-slate-800 text-slate-500 border border-slate-700/50 cursor-not-allowed'
              : 'bg-brand-green hover:bg-brand-green-dark text-dark-primary shadow-brand-green/10 hover:shadow-brand-green/30 hover:translate-y-[-1px]'
          }`}
        >
          {loading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Analyzing Narratives...</span>
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              <span>Predict Legitimacy</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
