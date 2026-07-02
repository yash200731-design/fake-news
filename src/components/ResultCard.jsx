import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle, BarChart3, ArrowUpRight, Search } from 'lucide-react';

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
            </div>
          </div>

          {/* Fact Check Skeleton */}
          <div className="pt-4 border-t border-dark-border/40 mt-4 space-y-2.5">
            <div className="h-3 rounded shimmer w-1/3" />
            <div className="p-4 rounded-xl bg-slate-950/45 border border-dark-border/20 space-y-2">
              <div className="h-3.5 rounded shimmer w-4/5" />
              <div className="h-3 rounded shimmer w-1/4" />
              <div className="h-3 rounded shimmer w-1/2" />
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

  const { prediction, ml_prediction, confidence, probabilities, isMock, fact_check, uncertain } = result;
  const isUncertain = uncertain || prediction === 'Prediction Uncertain';
  const isVerifiedReal = prediction === '✓ VERIFIED REAL';
  const isFake = prediction === 'Fake';

  // Dynamic Credibility & Risk calculations
  let credibilityScore = 50;
  if (isVerifiedReal) {
    credibilityScore = 100;
  } else if (prediction === 'Real') {
    credibilityScore = confidence;
  } else if (prediction === 'Prediction Uncertain') {
    credibilityScore = 50;
  } else if (prediction === 'Fake') {
    credibilityScore = Math.max(5, 100 - confidence);
  }

  let riskLevel = 'Medium';
  if (credibilityScore >= 75) {
    riskLevel = 'Low';
  } else if (credibilityScore < 40) {
    riskLevel = 'High';
  }

  let explanation = '';
  if (isVerifiedReal) {
    explanation = 'Matches verified news pattern. Cross-referenced and confirmed by independent fact-checking databases.';
  } else if (prediction === 'Real') {
    explanation = 'High similarity to trusted journalism. Style patterns match standard objective news formats.';
  } else if (prediction === 'Prediction Uncertain') {
    explanation = 'Linguistic traits are ambiguous. Writing exhibits a mix of informal assertions and reporting.';
  } else if (prediction === 'Fake') {
    if (confidence > 90) {
      explanation = 'No credible entities detected. Structure matches typical fabricated or unsubstantiated sources.';
    } else {
      explanation = 'Contains sensational language. Style patterns suggest emotional clickbait or speculation.';
    }
  }

  const formatReviewDate = (dateStr) => {
    if (!dateStr) return 'Unknown Date';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const getVerdictStyle = (verdict) => {
    const v = (verdict || '').toLowerCase();
    if (v.includes('false') || v.includes('fake') || v.includes('incorrect') || v.includes('misleading') || v.includes('untrue') || v.includes('debunked')) {
      return 'bg-red-500/15 text-red-400 border-red-500/20';
    }
    if (v.includes('true') || v.includes('correct') || v.includes('accurate') || v.includes('legitimate')) {
      return 'bg-brand-green/15 text-brand-green border-brand-green/20';
    }
    return 'bg-blue-500/15 text-brand-blue-light border-blue-500/20';
  };

  const renderHighlightedText = () => {
    if (!result.highlights || result.highlights.length === 0) {
      return null;
    }

    const textStr = result.text || '';
    const highlightMap = {};
    result.highlights.forEach(h => {
      highlightMap[h.word.toLowerCase()] = h.supports;
    });

    const tokens = textStr.split(/(\s+|\b)/);

    return (
      <div className="p-3.5 rounded-xl bg-slate-950/50 border border-dark-border/20 text-xs leading-relaxed max-h-44 overflow-y-auto font-sans text-text-secondary select-text">
        {tokens.map((token, idx) => {
          const cleanToken = token.trim().toLowerCase();
          if (cleanToken && highlightMap[cleanToken]) {
            const supports = highlightMap[cleanToken];
            return (
              <span 
                key={idx} 
                className={`px-1 rounded font-semibold border ${
                  supports === 'Real' 
                    ? 'bg-brand-green/20 text-brand-green border-brand-green/40' 
                    : supports === 'Fake'
                      ? 'bg-red-500/20 text-red-400 border-red-500/40'
                      : 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40'
                }`}
                title={`Supports ${supports}`}
              >
                {token}
              </span>
            );
          }
          return <span key={idx}>{token}</span>;
        })}
      </div>
    );
  };

  return (
    <div className={`w-full glass-panel rounded-2xl p-6 sm:p-8 border transition-all duration-500 h-full flex flex-col justify-between ${
      isUncertain
        ? 'border-amber-500/30 glow-yellow shadow-lg shadow-amber-950/10'
        : isFake 
          ? 'border-red-500/30 glow-blue shadow-lg shadow-red-950/10' 
          : 'border-brand-green/30 glow-green shadow-lg shadow-emerald-950/10'
    }`}>
      {/* Upper Content */}
      <div className="space-y-6">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-dark-border/40">
          <div className="flex items-center space-x-2">
            {isUncertain ? (
              <AlertTriangle className="w-6 h-6 text-amber-500 animate-pulse" />
            ) : isFake ? (
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

        {/* Verdict Badge */}
        <div className="text-center py-4 rounded-xl bg-slate-950/45 border border-dark-border/30">
          <span className="text-[10px] font-semibold text-text-muted uppercase tracking-widest block mb-1">
            Final Verdict
          </span>
          <h4 className={`font-display font-extrabold text-3xl tracking-wide uppercase ${
            isUncertain ? 'text-amber-500' : isFake ? 'text-red-500' : 'text-brand-green'
          }`}>
            {prediction}
          </h4>
          <p className="text-text-secondary text-xs mt-1.5 px-4 max-w-xs mx-auto leading-relaxed">
            {result.explanation && result.explanation.length > 0
              ? result.explanation.join(' ')
              : (isVerifiedReal
                  ? 'Overridden by confirmed Google Fact Check database. Fact-checkers verify this claim as true.'
                  : isUncertain
                    ? 'Linguistic style displays mixed structural features, making a confident classification impossible.'
                    : isFake 
                      ? 'High match with clickbait headers, unsubstantiated claims, or conspiracy syntax.'
                      : 'Consistent with peer-reviewed research structures, press bulletins, and factual reporting.')}
          </p>
        </div>

        {/* Verification Summary Panel */}
        <div className="p-4 rounded-xl bg-slate-950/40 border border-dark-border/20 space-y-2.5 text-xs">
          <div className="flex justify-between items-center pb-2 border-b border-dark-border/10">
            <span className="text-text-secondary font-semibold">Machine Learning Prediction</span>
            <span className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] uppercase border ${
              (ml_prediction || prediction) === 'Fake' 
                ? 'bg-red-500/15 text-red-400 border-red-500/20' 
                : (ml_prediction || prediction) === 'Prediction Uncertain' 
                  ? 'bg-amber-500/15 text-amber-400 border-amber-500/20' 
                  : 'bg-brand-green/15 text-brand-green border-brand-green/20'
            }`}>
              {ml_prediction || (isFake ? 'Fake' : 'Real')}
            </span>
          </div>
          
          <div className="flex justify-between items-center pb-2 border-b border-dark-border/10">
            <span className="text-text-secondary font-semibold">Google Fact Check Result</span>
            <span className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] uppercase border ${
              fact_check 
                ? getVerdictStyle(fact_check.verdict)
                : 'bg-slate-800/40 text-slate-400 border-slate-700/40'
            }`}>
              {fact_check ? fact_check.verdict : 'No verified fact check'}
            </span>
          </div>

          <div className="flex justify-between items-center pt-0.5">
            <span className="text-text-secondary font-semibold">Final Verdict</span>
            <span className={`px-2.5 py-0.5 rounded font-mono font-bold text-[10.5px] uppercase border ${
              isUncertain 
                ? 'bg-amber-500/15 text-amber-400 border-amber-500/20' 
                : isFake 
                  ? 'bg-red-500/15 text-red-400 border-red-500/20' 
                  : 'bg-brand-green/15 text-brand-green border-brand-green/20'
            }`}>
              {prediction}
            </span>
          </div>
        </div>

        {/* Credibility & Risk Assessment Panel */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Credibility Score Card */}
          <div className="p-4 rounded-xl bg-slate-950/30 border border-dark-border/20 flex flex-col items-center justify-center text-center">
            <span className="text-[10px] font-semibold text-text-muted uppercase tracking-widest block mb-2">Credibility Score</span>
            <div className="relative w-20 h-20 flex items-center justify-center">
              {/* Circular progress meter */}
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="40" cy="40" r="34" className="stroke-slate-800" strokeWidth="6" fill="transparent" />
                <circle cx="40" cy="40" r="34" 
                  className={`transition-all duration-1000 ease-out ${
                    riskLevel === 'High' ? 'stroke-red-500' : riskLevel === 'Medium' ? 'stroke-amber-500' : 'stroke-brand-green'
                  }`} 
                  strokeWidth="6" 
                  fill="transparent"
                  strokeDasharray="213.6"
                  strokeDashoffset={213.6 - (213.6 * credibilityScore) / 100}
                />
              </svg>
              <span className="absolute font-mono font-bold text-lg text-text-primary">{credibilityScore}%</span>
            </div>
          </div>

          {/* Risk Assessment Card */}
          <div className="p-4 rounded-xl bg-slate-950/30 border border-dark-border/20 flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-semibold text-text-muted uppercase tracking-widest block mb-1">Risk Assessment</span>
              <span className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide border ${
                riskLevel === 'High' 
                  ? 'bg-red-500/15 text-red-400 border-red-500/30' 
                  : riskLevel === 'Medium' 
                    ? 'bg-amber-500/15 text-amber-400 border-amber-500/30' 
                    : 'bg-brand-green/15 text-brand-green border-brand-green/30'
              }`}>
                {riskLevel} Risk
              </span>
            </div>
            <p className="text-[11px] text-text-secondary leading-relaxed mt-2">
              {explanation}
            </p>
          </div>
        </div>

        {/* LIME Explainability Highlights */}
        {result.highlights && result.highlights.length > 0 && (
          <div className="space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-semibold text-text-muted uppercase tracking-widest block">
                LIME Explainability Report
              </span>
              <span className="text-[9px] text-text-muted italic">Attribution Highlights</span>
            </div>
            
            {renderHighlightedText()}
            
            <div className="flex flex-wrap gap-3 text-[10px] text-text-secondary mt-1">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded bg-brand-green/20 border border-brand-green/45 inline-block" />
                Supports Real
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded bg-red-500/20 border border-red-500/45 inline-block" />
                Supports Fake
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded bg-yellow-500/20 border border-yellow-500/45 inline-block" />
                Neutral
              </span>
            </div>
          </div>
        )}

        {/* Confidence Percentage */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-text-secondary">Confidence:</span>
            <span className={`font-mono font-bold ${isUncertain ? 'text-amber-400' : isFake ? 'text-red-400' : 'text-brand-green-light'}`}>
              {confidence}%
            </span>
          </div>
          <div className="w-full bg-slate-950/70 h-3 rounded-full overflow-hidden p-0.5 border border-slate-800">
            <div 
              className={`h-full rounded-full relative overflow-hidden transition-all duration-1000 ease-out ${
                isUncertain ? 'bg-gradient-to-r from-yellow-500 to-amber-400' : isFake ? 'bg-gradient-to-r from-orange-500 to-red-500' : 'bg-gradient-to-r from-brand-green to-emerald-400'
              }`}
              style={{ width: `${confidence}%` }}
            >
              <div className="absolute inset-0 bg-white/10 animate-[pulse_2s_infinite] rounded-full" />
            </div>
          </div>
        </div>


        {/* Probability Breakdown Bar */}
        <div className="space-y-2 pt-1">
          <span className="text-xs font-semibold text-text-secondary uppercase tracking-widest block">
            Probability Distribution
          </span>
          
          <div className="grid grid-cols-2 gap-4">
            {/* Real Probability */}
            <div className="space-y-1">
              <div className="flex justify-between text-[11px] font-mono">
                <span className="text-text-secondary">Real:</span>
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
              <div className="flex justify-between text-[11px] font-mono">
                <span className="text-text-secondary">Fake:</span>
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

        {/* Google Fact Check Section */}
        <div className="pt-4 border-t border-dark-border/40 space-y-2.5">
          <div className="flex items-center space-x-1.5">
            <Search className="w-4 h-4 text-brand-green animate-pulse" />
            <span className="text-xs font-bold uppercase tracking-widest text-text-secondary">
              Google Fact-Check Database
            </span>
          </div>

          {fact_check ? (
            <div className="p-4 rounded-xl bg-slate-950/45 border border-dark-border/30 space-y-2.5 text-xs leading-relaxed hover:border-brand-green/20 transition-colors">
              <div>
                <span className="text-[10px] font-semibold text-text-muted block uppercase tracking-wider">Claim Reviewed</span>
                <p className="text-text-primary font-medium mt-0.5">"{fact_check.claim_title}"</p>
              </div>
              
              <div className="flex flex-wrap items-center justify-between gap-2 pt-1.5 border-t border-dark-border/10 mt-1">
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] text-text-muted uppercase">Fact Check Status:</span>
                  <span className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] border ${getVerdictStyle(fact_check.verdict)}`}>
                    {fact_check.verdict}
                  </span>
                </div>
                <span className="text-[10px] text-text-muted font-mono">
                  {formatReviewDate(fact_check.date)}
                </span>
              </div>
              
              <div className="pt-1 flex items-center justify-between text-[10px] text-text-muted">
                <span>Publisher: <strong className="text-text-secondary">{fact_check.publisher}</strong></span>
                <a 
                  href={fact_check.source_link} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="inline-flex items-center text-brand-green hover:underline font-bold text-xs gap-0.5"
                >
                  Source URL <ArrowUpRight className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="py-3 px-4 rounded-xl bg-slate-950/20 border border-dark-border/20 text-center">
                <span className="text-text-muted text-xs font-semibold">
                  No verified fact check available.
                </span>
              </div>
              
              {result.similar_news && result.similar_news.length > 0 && (
                <div className="space-y-2.5">
                  <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider block">
                    Similar Articles Found (Trusted Sources)
                  </span>
                  <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
                    {result.similar_news.map((item, idx) => (
                      <div key={idx} className="p-3 rounded-xl bg-slate-950/45 border border-dark-border/30 text-xs leading-relaxed space-y-1 hover:border-brand-green/20 transition-colors">
                        <div className="flex justify-between items-center">
                          <span className="text-[10px] font-bold text-brand-green uppercase tracking-wide">
                            {item.source}
                          </span>
                          <span className="text-[10px] text-text-muted font-mono">
                            {formatReviewDate(item.published_date)}
                          </span>
                        </div>
                        <h5 className="font-medium text-text-primary hover:text-brand-green transition-colors">
                          <a href={item.link} target="_blank" rel="noopener noreferrer" className="flex items-start gap-1">
                            {item.headline}
                            <ArrowUpRight className="w-3.5 h-3.5 flex-shrink-0 opacity-60" />
                          </a>
                        </h5>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

      </div>

      {/* Warning/Disclaimer */}
      <div className="pt-4 border-t border-dark-border/40 mt-6 flex items-start gap-2.5 text-[11px] text-text-secondary leading-relaxed">
        <AlertTriangle className={`w-4 h-4 flex-shrink-0 ${isUncertain ? 'text-amber-400' : isFake ? 'text-red-400' : 'text-brand-green'}`} />
        <span>
          AI findings should be corroborating evidence. Cross-reference claims with primary agencies (e.g. Snopes, AP, Reuters) before sharing online.
        </span>
      </div>
    </div>
  );
}
