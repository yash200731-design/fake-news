import axios from 'axios';

// Automatically use window.location.origin in production (Vercel) to query on the same domain,
// resolving CORS and mixed-content HTTPS -> HTTP browser blocks.
const API_URL = import.meta.env.VITE_API_URL !== undefined 
  ? import.meta.env.VITE_API_URL 
  : (typeof window !== 'undefined' && window.location.hostname === 'localhost' 
      ? 'http://localhost:8000' 
      : (typeof window !== 'undefined' ? window.location.origin : ''));

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Simulates a model prediction with simple keyword heuristics
 * to make the offline/mock mode feel realistic and intelligent.
 */
function simulatePrediction(text) {
  const textLower = text.toLowerCase();
  
  // Keyword analysis for demo
  const fakeKeywords = [
    'secret source', 'shocking truth', 'alien', 'conspiracy', 
    'scientists are quiet', 'miracle cure', '5g radiation', 
    'microchips', 'illuminati', 'hidden from the public', 'click here',
    'secret agenda', 'cured instantly', 'conspiracy theory', 'fake news'
  ];
  const realKeywords = [
    'researchers published', 'spokesperson stated', 'official reports', 
    'according to the study', 'health department', 'announced on wednesday',
    'global economy', 'scientific community', 'reuters', 'associated press',
    'parliament', 'senate', 'journal of medicine', 'spokesman', 'press conference'
  ];
  
  let fakeMatches = fakeKeywords.filter(keyword => textLower.includes(keyword)).length;
  let realMatches = realKeywords.filter(keyword => textLower.includes(keyword)).length;
  
  // Default probabilities
  let fakeProb = 0.5;
  let realProb = 0.5;
  
  if (fakeMatches > realMatches) {
    fakeProb = 0.72 + Math.random() * 0.22; // 72% to 94%
    realProb = 1 - fakeProb;
  } else if (realMatches > fakeMatches) {
    realProb = 0.74 + Math.random() * 0.21; // 74% to 95%
    fakeProb = 1 - realProb;
  } else {
    // If no keywords match, base on character length parity or random
    const lengthFactor = text.length % 2 === 0;
    if (lengthFactor) {
      realProb = 0.61 + Math.random() * 0.18;
      fakeProb = 1 - realProb;
    } else {
      fakeProb = 0.63 + Math.random() * 0.18;
      realProb = 1 - fakeProb;
    }
  }

  // Format probabilities to percentages (0-100)
  const isFake = fakeProb > realProb;
  const confidence = Math.round((isFake ? fakeProb : realProb) * 100);
  
  return {
    prediction: isFake ? 'Fake' : 'Real',
    confidence: confidence,
    probabilities: {
      Real: Math.round(realProb * 100),
      Fake: Math.round(fakeProb * 100)
    },
    isMock: true,
    timestamp: new Date().toISOString()
  };
}

/**
 * Predicts whether the news article is Real or Fake
 * @param {string} text - The content of the news article
 * @returns {Promise<{prediction: string, confidence: number, probabilities: {Real: number, Fake: number}, isMock: boolean, timestamp: string}>}
 */
export async function predictNews(text) {
  if (!text || text.trim().length < 15) {
    throw new Error('Input text is too short. Please paste a news article of at least 15 characters.');
  }

  try {
    const response = await api.post('/api/predict', { text });
    const data = response.data;
    
    // Support varying response shapes (e.g. fractional confidence or percentage confidence)
    let rawConf = data.confidence;
    let confidence = rawConf <= 1 ? Math.round(rawConf * 100) : Math.round(rawConf);
    
    let probReal = data.probabilities?.Real || (data.prediction === 'Real' ? confidence : 100 - confidence);
    let probFake = data.probabilities?.Fake || (data.prediction === 'Fake' ? confidence : 100 - confidence);

    // Normalize probabilities to 0-100
    probReal = probReal <= 1 ? Math.round(probReal * 100) : Math.round(probReal);
    probFake = probFake <= 1 ? Math.round(probFake * 100) : Math.round(probFake);

    return {
      prediction: data.prediction,
      ml_prediction: data.ml_prediction || data.prediction,
      confidence: confidence,
      uncertain: data.uncertain || false,
      probabilities: {
        Real: probReal,
        Fake: probFake
      },
      isMock: false,
      fact_check: data.fact_check || null,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    // If it's a backend response error, throw the exact backend message
    if (error.response) {
      const serverErrorMsg = error.response.data?.detail || error.message;
      throw new Error(`Backend Error: ${serverErrorMsg}`);
    }
    
    // If it's a network error (no response received), fallback to client simulation
    console.warn('FastAPI backend is offline or unreachable. Using client simulation fallback.', error);
    // Simulate API delay (1.2s) to show off loading animations
    await new Promise(resolve => setTimeout(resolve, 1200));
    return simulatePrediction(text);
  }
}

/**
 * Fetches latest verified news from NewsAPI (via the server proxy).
 * Falls back to structured mock data if the server is offline.
 */
export async function fetchNews(q = '', category = '') {
  try {
    const params = {};
    if (q) params.q = q;
    if (category && category !== 'all') params.category = category.toLowerCase();

    const response = await api.get('/api/news', { params });
    return response.data.articles || [];
  } catch (error) {
    console.warn('FastAPI backend is offline or returned an error. Using offline fallback news feed.', error);
    // Simulate minor network delay for loading feedback
    await new Promise(resolve => setTimeout(resolve, 600));
    return getOfflineNewsFallback(q, category);
  }
}

/**
 * Returns pre-packaged realistic verified news stories for the offline mode.
 */
function getOfflineNewsFallback(q = '', category = '') {
  const articles = [
    {
      title: "Voters Head to the Polls in Key Midterm Elections",
      description: "Local precincts report steady turnout as citizens vote on local budgets and school board candidates. Election officials confirmed all systems are operating securely.",
      source: { name: "Associated Press" },
      publishedAt: new Date(Date.now() - 3600000).toISOString(),
      url: "https://apnews.com",
      urlToImage: "https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=600&auto=format&fit=crop&q=60"
    },
    {
      title: "Global Tech Summit Highlights Latest AI Advancements",
      description: "Tech leaders gathered in Silicon Valley to showcase generative models, database architectures, and next-generation neural chips. Focus remains on developer utility.",
      source: { name: "TechCrunch" },
      publishedAt: new Date(Date.now() - 7200000).toISOString(),
      url: "https://techcrunch.com",
      urlToImage: "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=60"
    },
    {
      title: "NASA Weather Satellite Transmits First High-Res Climate Scans",
      description: "Mission control confirmed the telemetry signals from the newly launched climate satellite are healthy, enabling real-time storm and ocean wave observations.",
      source: { name: "NASA" },
      publishedAt: new Date(Date.now() - 14400000).toISOString(),
      url: "https://nasa.gov",
      urlToImage: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&auto=format&fit=crop&q=60"
    },
    {
      title: "Medical Journal Publishes Breakthrough Cancer Therapy Results",
      description: "Researchers detailed the outcomes of a clinical phase-II trial for targeted immunotherapies, showing promising remission metrics across patient trials.",
      source: { name: "Journal of Medicine" },
      publishedAt: new Date(Date.now() - 86400000).toISOString(),
      url: "https://nejm.org",
      urlToImage: "https://images.unsplash.com/photo-1579684389782-64d84b5e901a?w=600&auto=format&fit=crop&q=60"
    },
    {
      title: "Central Bank Keeps Benchmark Rates Unchanged",
      description: "The Federal Reserve cited stable job growth and moderating consumer indices as the core reasons to maintain target rates, stabilizing local bond markets.",
      source: { name: "Reuters" },
      publishedAt: new Date(Date.now() - 172800000).toISOString(),
      url: "https://reuters.com",
      urlToImage: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=600&auto=format&fit=crop&q=60"
    },
    {
      title: "Championship Marathon Welcomes Over Ten Thousand Runners",
      description: "Superb weather conditions and high turnouts marked the annual city run. Local authorities managed detours smoothly, thanking hundreds of water volunteers.",
      source: { name: "ESPN" },
      publishedAt: new Date(Date.now() - 259200000).toISOString(),
      url: "https://espn.com",
      urlToImage: "https://images.unsplash.com/photo-1502224562085-639556652f33?w=600&auto=format&fit=crop&q=60"
    }
  ];

  let filtered = articles;
  
  if (category && category !== 'all') {
    const catMap = {
      business: ["reuters"],
      technology: ["techcrunch"],
      science: ["nasa"],
      health: ["journal of medicine"],
      sports: ["espn"],
      general: ["associated press"]
    };
    const allowedSources = catMap[category.toLowerCase()] || [];
    filtered = articles.filter(a => allowedSources.includes(a.source.name.toLowerCase()));
  }

  if (q) {
    const ql = q.toLowerCase();
    filtered = filtered.filter(a => a.title.toLowerCase().includes(ql) || a.description.toLowerCase().includes(ql));
  }

  return filtered;
}
