import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import PredictForm from './components/PredictForm';
import ResultCard from './components/ResultCard';
import History from './components/History';
import Features from './components/Features';
import About from './components/About';
import FAQ from './components/FAQ';
import Contact from './components/Contact';
import Footer from './components/Footer';
import Toast from './components/Toast';
import NewsFeed from './components/NewsFeed';
import { predictNews } from './services/api';


function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [externalText, setExternalText] = useState('');
  
  // Theme state synced with local storage or browser preference
  const [theme, setTheme] = useState(() => {
    try {
      const savedTheme = localStorage.getItem('veritruth_theme');
      if (savedTheme) return savedTheme;
      return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    } catch {
      return 'dark';
    }
  });

  // Toasts queue state
  const [toasts, setToasts] = useState([]);

  // Sync theme class with document element
  useEffect(() => {
    try {
      const root = window.document.documentElement;
      if (theme === 'light') {
        root.classList.add('light');
        root.classList.remove('dark');
      } else {
        root.classList.add('dark');
        root.classList.remove('light');
      }
      localStorage.setItem('veritruth_theme', theme);
    } catch (err) {
      console.error('Failed to sync theme with document element', err);
    }
  }, [theme]);

  // Load prediction history from local storage on mount
  useEffect(() => {
    try {
      const savedHistory = localStorage.getItem('veritruth_history');
      if (savedHistory) {
        setHistory(JSON.parse(savedHistory));
      }
    } catch (err) {
      console.error('Failed to load history from localStorage', err);
    }
  }, []);

  const addToast = (message, type = 'info') => {
    const id = Date.now().toString() + Math.random().toString(36).substring(2, 5);
    setToasts((prevToasts) => [...prevToasts, { id, message, type }]);
  };

  const removeToast = (id) => {
    setToasts((prevToasts) => prevToasts.filter((t) => t.id !== id));
  };

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    addToast(`Switched to ${newTheme === 'dark' ? 'Dark' : 'Light'} Mode`, 'info');
  };

  const handlePredict = async (text) => {
    setError(null);
    setLoading(true);
    setResult(null);
    addToast('Starting narrative logic evaluation...', 'info');

    try {
      const data = await predictNews(text);
      setResult(data);
      addToast('Analysis complete. Verdict generated!', 'success');

      // Create history entry
      const newHistoryItem = {
        id: Date.now().toString(),
        text: text,
        prediction: data.prediction,
        confidence: data.confidence,
        probabilities: data.probabilities,
        isMock: data.isMock,
        fact_check: data.fact_check,
        timestamp: data.timestamp
      };

      const updatedHistory = [newHistoryItem, ...history].slice(0, 10); // Keep last 10 entries
      setHistory(updatedHistory);
      localStorage.setItem('veritruth_history', JSON.stringify(updatedHistory));
    } catch (err) {
      const errMsg = err.message || 'An unexpected error occurred during prediction.';
      setError(errMsg);
      addToast(errMsg, 'error');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectArticle = (text, item) => {
    setExternalText(text);
    setResult({
      prediction: item.prediction,
      confidence: item.confidence,
      probabilities: item.probabilities || {
        Real: item.prediction === 'Real' ? item.confidence : 100 - item.confidence,
        Fake: item.prediction === 'Fake' ? item.confidence : 100 - item.confidence
      },
      isMock: item.isMock !== undefined ? item.isMock : true,
      fact_check: item.fact_check,
      timestamp: item.timestamp
    });
    addToast('Past prediction reloaded into analyzer.', 'success');
    
    // Smooth scroll back to input form
    const element = document.getElementById('analyze');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleClearHistory = () => {
    setHistory([]);
    localStorage.removeItem('veritruth_history');
    addToast('Analysis history cleared.', 'info');
  };

  const handleVerifyNews = (text) => {
    setExternalText(text);
    addToast('Article copied. Triggering automatic AI analysis...', 'info');
    
    // Smooth scroll back to input form
    const element = document.getElementById('analyze');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Automatically trigger the classification
    handlePredict(text);
  };


  return (
    <div className="min-h-screen flex flex-col bg-dark-primary text-text-primary font-sans selection:bg-brand-green/30 selection:text-white transition-colors duration-300">
      {/* Sticky Glassmorphic Navbar */}
      <Navbar theme={theme} onToggleTheme={toggleTheme} />

      {/* Main Hero Section */}
      <Hero />

      {/* Analyzer Dashboard Container */}
      <main className="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        
        {/* Analyze Interactive Section */}
        <section id="analyze" className="py-16 border-t border-dark-border/40 scroll-mt-24">
          
          {/* Header */}
          <div className="text-center max-w-3xl mx-auto mb-12 space-y-3">
            <span className="text-xs font-semibold text-brand-green uppercase tracking-widest bg-brand-green/10 border border-brand-green/20 px-3.5 py-1 rounded-full">
              Interactive Dashboard
            </span>
            <h2 className="font-display font-extrabold text-3xl sm:text-4xl text-text-primary">
              Verify Article Legitimacy
            </h2>
            <p className="text-text-secondary text-sm sm:text-base max-w-lg mx-auto">
              Paste the text of a blog, column, or report below. Our classifier will analyze linguistic features to assign an integrity score.
            </p>
          </div>

          {/* Grid: Form and ResultCard */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
            
            {/* Form Column */}
            <div className="lg:col-span-7 flex flex-col gap-6">
              <PredictForm 
                onPredict={handlePredict} 
                loading={loading} 
                error={error} 
                externalText={externalText}
              />
              <History 
                history={history} 
                onSelectArticle={handleSelectArticle} 
                onClearHistory={handleClearHistory}
              />
            </div>

            {/* Result Report Column */}
            <div className="lg:col-span-5">
              <ResultCard result={result} loading={loading} />
            </div>

          </div>
        </section>

        {/* News Feed Section */}
        <section id="news" className="py-16 border-t border-dark-border/40 scroll-mt-24">
          <NewsFeed onVerifyNews={handleVerifyNews} />
        </section>

        {/* Features Section */}
        <Features />

        {/* About Section */}
        <About />

        {/* FAQ Section */}
        <FAQ />

        {/* Contact Section */}
        <Contact onSubmitSuccess={() => addToast('Inquiry message sent successfully!', 'success')} />

      </main>

      {/* Footer Section */}
      <Footer />

      {/* Toast Notifications */}
      <Toast toasts={toasts} onClose={removeToast} />
    </div>
  );
}

export default App;
