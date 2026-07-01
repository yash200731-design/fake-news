import React from 'react';
import { History as HistoryIcon, Trash2, ArrowUpRight, ShieldCheck, ShieldAlert } from 'lucide-react';

export default function History({ history, onSelectArticle, onClearHistory }) {
  const formatDate = (isoString) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' ' + 
             date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    } catch {
      return 'Just now';
    }
  };

  if (!history || history.length === 0) {
    return (
      <div className="w-full glass-panel rounded-2xl p-6 border border-white/10 text-center flex flex-col items-center justify-center min-h-[220px]">
        <HistoryIcon className="w-10 h-10 text-text-muted mb-2.5" />
        <h4 className="font-display font-semibold text-sm text-text-primary">No History Yet</h4>
        <p className="text-text-secondary text-xs max-w-xs mt-1">
          Your analyzed articles will be saved here in local storage for quick retrieval.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full glass-panel rounded-2xl p-6 border border-white/10 flex flex-col space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-dark-border/40">
        <div className="flex items-center space-x-2">
          <HistoryIcon className="w-5 h-5 text-brand-green" />
          <h4 className="font-display font-bold text-sm text-text-primary">Recent Analyses</h4>
        </div>
        <button
          onClick={onClearHistory}
          className="text-text-secondary hover:text-red-400 hover:bg-red-500/10 p-1.5 rounded-lg transition-all cursor-pointer flex items-center space-x-1 text-xs"
          title="Clear all history"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Clear</span>
        </button>
      </div>

      {/* List */}
      <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
        {history.map((item, index) => {
          const isFake = item.prediction === 'Fake';
          return (
            <div
              key={item.id || index}
              className="p-3 rounded-xl bg-dark-primary/30 hover:bg-dark-primary/65 border border-dark-border hover:border-brand-green/30 transition-all duration-200 group flex items-start justify-between gap-3 text-xs"
            >
              {/* Left Column: Verdict Badge & snippet */}
              <div className="flex-1 min-w-0 space-y-1">
                <div className="flex items-center space-x-2">
                  <span className={`inline-flex items-center space-x-1 font-mono font-bold tracking-wider px-2 py-0.5 rounded text-[10px] uppercase ${
                    isFake 
                      ? 'bg-red-500/15 text-red-400 border border-red-500/20' 
                      : 'bg-brand-green/15 text-brand-green border border-brand-green/20'
                  }`}>
                    {isFake ? (
                      <ShieldAlert className="w-2.5 h-2.5" />
                    ) : (
                      <ShieldCheck className="w-2.5 h-2.5" />
                    )}
                    <span>{item.prediction}</span>
                  </span>
                  <span className="text-[10px] text-text-muted font-mono">
                    {formatDate(item.timestamp)}
                  </span>
                </div>
                <p className="text-text-primary font-sans truncate text-[11px] mt-1 pr-2">
                  {item.text}
                </p>
              </div>

              {/* Right Column: Confidence and Autofill trigger */}
              <div className="flex flex-col items-end justify-between self-stretch text-right min-w-[55px]">
                <span className={`font-mono font-bold ${isFake ? 'text-red-400' : 'text-brand-green-light'}`}>
                  {item.confidence}%
                </span>
                <button
                  onClick={() => onSelectArticle(item.text, item)}
                  className="text-text-muted hover:text-brand-green group-hover:text-text-secondary transition-colors p-0.5 cursor-pointer"
                  title="Reload this article"
                >
                  <ArrowUpRight className="w-4 h-4 transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
