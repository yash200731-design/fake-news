import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle, HelpCircle, BarChart3 } from 'lucide-react';

export default function ResultCard({ result }) {
  if (!result) {
    return (
      <div className="w-full glass-panel rounded-2xl p-8 border border-white/10 border-dashed flex flex-col items-center justify-center text-center h-full min-h-[380px]">
        <div className="w-16 h-16 rounded-2xl bg-slate-900 flex items-center justify-center border border-dark-border mb-4">
          <BarChart3 className="w-8 h-8 text-slate-500" />
        </div>
        <h3 className="font-display font-semibold text-lg text-slate-200">Awaiting Analysis</h3>
        <p className="text-slate-400 text-sm max-w-xs mt-2 leading-relaxed">
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
            <span className="font-display font-bold text-base uppercase tracking-widest text-slate-300">
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
          <p className="text-slate-400 text-xs mt-1.5 px-4 max-w-xs mx-auto leading-relaxed">
            {isFake 
              ? 'High match with clickbait headers, unsubstantiated claims, or rumor syntax.'
              : 'Consistent with peer-reviewed research structures, press bulletins, and factual reporting.'}
          </p>
        </div>

        {/* Confidence Percentage */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">Model Confidence Rating:</span>
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
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest block">
            Probability Distribution
          </span>
          
          <div className="space-y-3">
            {/* Real Probability */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300">Legitimate (Real):</span>
                <span className="text-slate-200 font-bold">{probabilities.Real}%</span>
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
                <span className="text-slate-300">Unverifiable (Fake):</span>
                <span className="text-slate-200 font-bold">{probabilities.Fake}%</span>
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

      {/* Warning/Disclaimer Disclaimer */}
      <div className="pt-4 border-t border-dark-border/40 mt-4 flex items-start gap-2.5 text-[11px] text-slate-400 leading-relaxed">
        <AlertTriangle className={`w-4 h-4 flex-shrink-0 ${isFake ? 'text-red-400' : 'text-brand-green'}`} />
        <span>
          AI findings should be corroborating evidence. Cross-reference claims with primary agencies (e.g. Snopes, AP, Reuters) before sharing online.
        </span>
      </div>
    </div>
  );
}
