import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle, BarChart3 } from 'lucide-react';

export default function ResultCard({ result, loading }) {
  // Skeleton Loader State
  if (loading) {
    return (
      <div className="w-full glass-panel rounded-2xl p-6 sm:p-8 border border-white/10 glow-green h-full flex flex-col justify-between min-h-[380px]">
        <div className="space-y-6 flex-grow">
          {/* Header Skeleton */}
          <div className="flex items-center justify-between pb-3 border-b border-dark-border/40">
            <div className="flex items-center space-x-2 w-1/2">
              <div className="w-5 h-5 rounded-lg shimmer flex-shrink-0" />
              <div className="h-4 rounded shimmer w-3/4" />
            </div>
            <div className="h-4 rounded shimmer w-1/4" />
          </div>

          {/* Verdict Banner Skeleton */}
          <div className="py-7 rounded-xl bg-slate-950/45 border border-dark-border/30 flex flex-col items-center justify-center space-y-3">
            <div className="h-3 rounded shimmer w-1/5" />
            <div className="h-7 rounded shimmer w-1/2" />
            <div className="h-3 rounded shimmer w-2/3" />
          </div>

          {/* Confidence Slider Skeleton */}
          <div className="space-y-2">
            <div className="flex justify-between">
              <div className="h-3 rounded shimmer w-1/3" />
              <div className="h-3 rounded shimmer w-1/12" />
            </div>
            <div className="w-full h-3 rounded-full shimmer" />
          </div>

          {/* Probabilities Skeleton */}
          <div className="space-y-3 pt-2">
            <div className="h-3 rounded shimmer w-1/4" />
            <div className="space-y-3">
              <div className="space-y-1">
                <div className="flex justify-between">
                  <div className="h-2 rounded shimmer w-1/5" />
                  <div className="h-2 rounded shimmer w-1/12" />
                </div>
                <div className="w-full h-2 rounded-full shimmer" />
              </div>
              <div className="space-y-1">
                <div className="flex justify-between">
                  <div className="h-2 rounded shimmer w-1/5" />
                  <div className="h-2 rounded shimmer w-1/12" />
                </div>
                <div className="w-full h-2 rounded-full shimmer" />
              </div>
            </div>
          </div>
        </div>

        {/* Disclaimer Skeleton */}
        <div className="pt-4 border-t border-dark-border/40 mt-6 flex items-start gap-2.5">
          <div className="w-4 h-4 rounded shimmer flex-shrink-0" />
          <div className="flex-1 space-y-1.5">
            <div className="h-2 rounded shimmer w-full" />
            <div className="h-2 rounded shimmer w-5/6" />
          </div>
        </div>
      </div>
    );
  }

  // Awaiting Input State
  if (!result) {
    return (
      <div className="w-full glass-panel rounded-2xl p-8 border border-white/10 border-dashed flex flex-col items-center justify-center text-center h-full min-h-[380px]">
        <div className="w-16 h-16 rounded-2xl bg-slate-900 flex items-center justify-center border border-dark-border mb-4">
          <BarChart3 className="w-8 h-8 text-slate-500" />
        </div>
        <h3 className="font-display font-semibold text-lg text-text-primary">Awaiting Analysis</h3>
        <p className="text-text-secondary text-sm max-w-xs mt-2 leading-relaxed">
          Paste a news article and click "Predict Legitimacy" to see AI-powered model classification reports.
        </p>
      </div>
    );
  }

  const { prediction, confidence, probabilities, isMock } = result;
  const isFake = prediction === 'Fake';

  return (
    <div className={`w-full glass-panel rounded-2xl p-6 sm:p-8 border transition-all duration-500 h-full flex flex-col justify-between ${
      isFake 
        ? 'border-red-500/30 glow-blue shadow-lg shadow-red-950/10' 
        : 'border-brand-green/30 glow-green shadow-lg shadow-emerald-950/10'
    }`}>
      {/* Header */}
      <div className="space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-dark-border/40">
          <div className="flex items-center space-x-2">
            {isFake ? (
              <ShieldAlert className="w-6 h-6 text-red-500" />
            ) : (
              <ShieldCheck className="w-6 h-6 text-brand-green" />
            )}
            <span className="font-display font-bold text-base uppercase tracking-widest text-text-secondary">
              Analysis Report
            </span>
          </div>
          {isMock && (
            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono border border-slate-700/60">
              Offline Demo
            </span>
          )}
        </div>

        {/* Big Flag Category */}
        <div className="text-center py-5 rounded-xl bg-slate-950/45 border border-dark-border/30">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest block mb-1">
            Verdict
          </span>
          <h4 className={`font-display font-extrabold text-3xl tracking-wide uppercase ${
            isFake ? 'text-red-500' : 'text-brand-green'
          }`}>
            {isFake ? 'Fake News' : 'Verified Real'}
          </h4>
          <p className="text-text-secondary text-xs mt-1.5 px-4 max-w-xs mx-auto leading-relaxed">
            {isFake 
              ? 'High match with clickbait headers, unsubstantiated claims, or rumor syntax.'
              : 'Consistent with peer-reviewed research structures, press bulletins, and factual reporting.'}
          </p>
        </div>

        {/* Confidence Percentage */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-text-secondary">Model Confidence Rating:</span>
            <span className={`font-mono font-bold ${isFake ? 'text-red-400' : 'text-brand-green-light'}`}>
              {confidence}%
            </span>
          </div>
          <div className="w-full bg-slate-950/70 h-3 rounded-full overflow-hidden p-0.5 border border-slate-800">
            <div 
              className={`h-full rounded-full transition-all duration-1000 ease-out ${
                isFake ? 'bg-gradient-to-r from-orange-500 to-red-500' : 'bg-gradient-to-r from-brand-green to-emerald-400'
              }`}
              style={{ width: `${confidence}%` }}
            />
          </div>
        </div>

        {/* Probability Breakdown Bar */}
        <div className="space-y-2 pt-2">
          <span className="text-xs font-semibold text-text-secondary uppercase tracking-widest block">
            Probability Distribution
          </span>
          
          <div className="space-y-3">
            {/* Real Probability */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-text-secondary">Legitimate (Real):</span>
                <span className="text-text-primary font-bold">{probabilities.Real}%</span>
              </div>
              <div className="w-full bg-slate-950/40 h-2 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-brand-green rounded-full transition-all duration-1000"
                  style={{ width: `${probabilities.Real}%` }}
                />
              </div>
            </div>

            {/* Fake Probability */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-text-secondary">Unverifiable (Fake):</span>
                <span className="text-text-primary font-bold">{probabilities.Fake}%</span>
              </div>
              <div className="w-full bg-slate-950/40 h-2 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-red-500 rounded-full transition-all duration-1000"
                  style={{ width: `${probabilities.Fake}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Warning/Disclaimer */}
      <div className="pt-4 border-t border-dark-border/40 mt-4 flex items-start gap-2.5 text-[11px] text-text-secondary leading-relaxed">
        <AlertTriangle className={`w-4 h-4 flex-shrink-0 ${isFake ? 'text-red-400' : 'text-brand-green'}`} />
        <span>
          AI findings should be corroborating evidence. Cross-reference claims with primary agencies (e.g. Snopes, AP, Reuters) before sharing online.
        </span>
      </div>
    </div>
  );
}
