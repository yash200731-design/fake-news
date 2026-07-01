const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
    const response = await fetch(`${API_URL}/api/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.statusText}`);
    }

    const data = await response.json();
    
    // Support varying response shapes (e.g. fractional confidence or percentage confidence)
    let rawConf = data.confidence;
    let confidence = rawConf <= 1 ? Math.round(rawConf * 100) : Math.round(rawConf);
    
    let probReal = data.probabilities?.Real || (data.prediction === 'Real' ? confidence : 100 - confidence);
    let probFake = data.probabilities?.Fake || (data.prediction === 'Fake' ? confidence : 100 - confidence);

    // Normalize probabilities to 0-100
    probReal = probReal <= 1 ? Math.round(probReal * 100) : Math.round(probReal);
    probFake = probFake <= 1 ? Math.round(probFake * 100) : Math.round(probFake);

    return {
      prediction: data.prediction, // Expects "Real" or "Fake"
      confidence: confidence,
      probabilities: {
        Real: probReal,
        Fake: probFake
      },
      isMock: false,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    console.warn('FastAPI backend is offline or returned an error. Using client simulation fallback.', error);
    // Simulate API delay (1.2s) to show off loading animations
    await new Promise(resolve => setTimeout(resolve, 1200));
    return simulatePrediction(text);
  }
}
