import React, { useState, useEffect } from 'react';
import { Search, Globe, Calendar, ArrowUpRight, CheckCircle2, RotateCcw } from 'lucide-react';
import { fetchNews } from '../services/api';

const CATEGORIES = [
  { id: 'all', name: 'All News' },
  { id: 'business', name: 'Business' },
  { id: 'technology', name: 'Technology' },
  { id: 'science', name: 'Science' },
  { id: 'health', name: 'Health' },
  { id: 'sports', name: 'Sports' }
];

export default function NewsFeed({ onVerifyNews }) {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');
  const [error, setError] = useState(null);

  const loadArticles = async (query = '', category = 'all') => {
    setLoading(true);
    setError(null);
    try {
      const articles = await fetchNews(query, category);
      // Filter out removed/dead articles (common in NewsAPI responses)
      const validArticles = articles.filter(
        (a) => a.title && a.title !== '[Removed]' && a.description !== '[Removed]'
      );
      setNews(validArticles);
    } catch (err) {
      setError('Could not retrieve latest news. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadArticles(searchTerm, activeCategory);
  }, [activeCategory]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadArticles(searchTerm, activeCategory);
  };

  const handleResetSearch = () => {
    setSearchTerm('');
    setActiveCategory('all');
    loadArticles('', 'all');
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="space-y-8">
      {/* Feed Title and Controls */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-dark-border/40">
        <div className="space-y-1.5">
          <div className="flex items-center space-x-2">
            <Globe className="w-5 h-5 text-brand-green animate-spin" style={{ animationDuration: '12s' }} />
            <h2 className="font-display font-extrabold text-2xl tracking-wide uppercase text-text-primary">
              Verified News Portal
            </h2>
          </div>
          <p className="text-text-secondary text-sm max-w-xl">
            Browse verified real-time articles from global media agencies. Use the AI toolkit to analyze writing structures.
          </p>
        </div>

        {/* Search & Reset Inputs */}
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 max-w-md w-full md:w-auto">
          <div className="relative flex-grow">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search news keywords..."
              className="w-full bg-slate-950/60 border border-dark-border/60 hover:border-dark-border focus:border-brand-green focus:outline-none rounded-xl py-2.5 pl-10 pr-4 text-sm text-text-primary transition-colors duration-200 placeholder:text-text-muted"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2.5 bg-slate-900 border border-dark-border hover:bg-slate-800 text-text-primary rounded-xl text-sm font-semibold transition-colors duration-200"
          >
            Search
          </button>
          {(searchTerm || activeCategory !== 'all') && (
            <button
              type="button"
              onClick={handleResetSearch}
              title="Reset Filters"
              className="p-2.5 bg-slate-950/40 border border-dark-border/40 hover:bg-slate-900 text-text-muted hover:text-text-primary rounded-xl transition-colors duration-200 flex items-center justify-center"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          )}
        </form>
      </div>

      {/* Category Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-thin">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id)}
            className={`px-4 py-2 rounded-full text-xs font-bold transition-all duration-300 uppercase tracking-widest whitespace-nowrap border ${
              activeCategory === cat.id
                ? 'bg-brand-green text-white border-brand-green shadow-md shadow-emerald-950/20 scale-105'
                : 'bg-slate-950/45 text-text-secondary border-dark-border/40 hover:border-brand-green/30 hover:text-text-primary'
            }`}
          >
            {cat.name}
          </button>
        ))}
      </div>

      {/* News Articles Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((idx) => (
            <div key={idx} className="glass-panel border border-white/5 rounded-2xl overflow-hidden min-h-[360px] flex flex-col justify-between p-4 space-y-4">
              <div className="space-y-3">
                <div className="w-full h-44 rounded-xl shimmer" />
                <div className="flex justify-between">
                  <div className="h-3 rounded shimmer w-1/4" />
                  <div className="h-3 rounded shimmer w-1/4" />
                </div>
                <div className="h-4 rounded shimmer w-5/6" />
                <div className="h-3 rounded shimmer w-full" />
                <div className="h-3 rounded shimmer w-4/5" />
              </div>
              <div className="h-9 rounded shimmer w-full" />
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="py-12 text-center glass-panel rounded-2xl border border-red-500/20 bg-red-950/5">
          <p className="text-red-400 font-semibold">{error}</p>
          <button
            onClick={() => loadArticles(searchTerm, activeCategory)}
            className="mt-4 px-4 py-2 bg-slate-900 border border-dark-border hover:bg-slate-800 rounded-lg text-xs font-bold text-text-primary transition-colors duration-200"
          >
            Retry Fetch
          </button>
        </div>
      ) : news.length === 0 ? (
        <div className="py-16 text-center glass-panel rounded-2xl border border-white/5">
          <p className="text-text-muted text-sm font-medium">No verified news matches your query criteria.</p>
          <button
            onClick={handleResetSearch}
            className="mt-4 px-4 py-2 bg-brand-green/20 border border-brand-green/30 hover:bg-brand-green/30 rounded-xl text-xs font-bold text-brand-green transition-all duration-200"
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {news.map((article, idx) => (
            <div
              key={idx}
              className="glass-panel border border-white/10 hover:border-brand-green/30 rounded-2xl overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-emerald-950/5 flex flex-col h-full justify-between"
            >
              {/* Card Image and Publisher Info */}
              <div>
                <div className="relative w-full h-44 bg-slate-950 overflow-hidden border-b border-dark-border/40">
                  {article.urlToImage ? (
                    <img
                      src={article.urlToImage}
                      alt={article.title}
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&auto=format&fit=crop&q=60';
                      }}
                      className="w-full h-full object-cover hover:scale-105 transition-transform duration-500"
                    />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-slate-950 to-slate-900 flex items-center justify-center">
                      <Globe className="w-12 h-12 text-slate-800" />
                    </div>
                  )}
                  <span className="absolute top-3 left-3 px-2.5 py-1 rounded-lg bg-slate-950/85 backdrop-blur-sm border border-white/10 text-[10px] font-bold text-brand-green uppercase tracking-wider">
                    {article.source?.name || 'News Source'}
                  </span>
                </div>

                {/* Card Text Content */}
                <div className="p-5 space-y-3">
                  <div className="flex items-center text-text-muted text-[10px] space-x-1.5 font-mono">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{formatDate(article.publishedAt)}</span>
                  </div>

                  <h3 className="font-display font-bold text-sm text-text-primary leading-snug line-clamp-2 hover:text-brand-green transition-colors">
                    <a href={article.url} target="_blank" rel="noopener noreferrer" className="flex items-start gap-1">
                      {article.title}
                      <ArrowUpRight className="w-4 h-4 flex-shrink-0 opacity-40 hover:opacity-100" />
                    </a>
                  </h3>

                  <p className="text-text-secondary text-xs leading-relaxed line-clamp-3">
                    {article.description || 'No description available for this article.'}
                  </p>
                </div>
              </div>

              {/* Action Footer */}
              <div className="p-5 pt-0">
                <button
                  onClick={() => onVerifyNews(article.description || article.title)}
                  className="w-full py-2 bg-slate-950 border border-dark-border/80 hover:border-brand-green/30 hover:bg-slate-900 text-brand-green hover:text-emerald-400 rounded-xl text-xs font-bold transition-all duration-300 flex items-center justify-center gap-1.5"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  Verify with AI
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
