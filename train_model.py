import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Realistic training corpus representing real and fake news indicators
# 0 = Real News, 1 = Fake News / Misinformation
corpus = [
    # --- REAL NEWS ---
    ("Researchers published a new peer-reviewed study on Wednesday in the Journal of Medicine detailing the impact of global trade shifts on local agricultural economies. According to the study, official reports from the agriculture department show a steady recovery in farm yields. A spokesperson stated that a press conference will be held next week to discuss long-term crop sustainability programs and water management reforms.", 0),
    ("The Federal Reserve announced on Thursday that it is keeping interest rates unchanged, citing steady economic growth and moderating inflation. The central bank stated that it remains committed to its target rate and will monitor economic indicators closely in the coming months.", 0),
    ("Local authorities confirmed that the highway expansion project has been completed ahead of schedule. The transportation department issued a statement confirming that all lanes are now open to commuter traffic, which is expected to ease congestion in the metro area.", 0),
    ("A spokesperson for the World Health Organization announced that a new initiative has been launched to combat infectious diseases in developing nations. The global program will distribute vaccines, medical supplies, and provide clinical training to local healthcare workers.", 0),
    ("Major tech companies reported their quarterly earnings reports, showing solid revenue growth driven by cloud computing divisions. Analysts noted that demand for database and cloud storage services remains strong across global corporate sectors.", 0),
    ("According to official reports, the metropolitan school board approved a new budget for the upcoming academic year. The funding will support classroom improvements, teacher salaries, and digital learning platforms across all public school districts.", 0),
    ("The National Space Agency successfully launched a weather satellite into orbit on Tuesday evening. Mission control confirmed that the telemetry signals are healthy and the satellite has deployed its solar arrays for power collection.", 0),
    ("A panel of international economists released a statement urging governments to invest in renewable energy infrastructure. The study suggests that long-term transition policies will create jobs and stabilize global energy markets.", 0),
    ("The city council voted to approve a new zoning layout that allows for the construction of affordable housing units downtown. Municipal officials said the development plans include green spaces and pedestrian pathways.", 0),
    ("In a press conference today, the foreign ministry declared that bilateral talks have successfully concluded, leading to a new trade agreement. The treaty is designed to lower tariffs on agricultural imports and exports.", 0),

    # --- FAKE NEWS / MISINFORMATION ---
    ("SHOCKING TRUTH: A secret source has confirmed that alien spacecraft have landed in a hidden desert base. The government is keeping this quiet to hide the miracle technologies which could cure all illnesses instantly. Scientists are quiet because they are being controlled by the Illuminati who want to enforce 5G radiation microchips on the entire global population. Share this before it gets taken down by the media!", 1),
    ("MIRACLE CURE EXPOSED: Doctors are furious that this simple secret home remedy is curing cancer in just 24 hours. The pharmaceutical industry is trying to ban this organic recipe to protect their corporate profits. Click this link right now to find out the shocking recipe before they delete it forever!", 1),
    ("MUST READ: Secret government documents leaked online prove that the earth is actually hollow and a advanced civilization lives inside it. Major media channels are refusing to report this mind-blowing discovery because they are controlled by corrupt politicians! Share this post with everyone you know!", 1),
    ("BREAKING NEWS: A massive conspiracy has been uncovered. Big tech companies are using your smart devices to project secret subliminal waves that control your thoughts and force you to buy their products. A whistleblower has escaped and revealed the whole truth in a shocking video!", 1),
    ("WARNING: A secret chemical is being sprayed in our drinking water to make citizens submissive to a global dictatorship. Scientists who tried to warning the public have gone missing mysteriously. Buy our filtration kit today to protect your family from this hidden threat!", 1),
    ("ANONYMOUS SOURCE CLAIMS: The presidential election was completely simulated by supercomputers. No real votes were counted, and the results were decided months in advance by a cabal of bankers. Share this immediately before the censors wipe it from the internet!", 1),
    ("SHOCKING DISCOVERY: Eating this common fruit immediately immunizes you to all types of viruses and disease. The government does not want you to know about this because they make billions from hospital visits. Reveal the secret truth by sharing this with ten friends!", 1),
    ("Leaked footage shows that space agencies staged all moon landings in a television studio. The fake videos were created to win the space race. Watch this hidden video evidence showing the directors and studio setups before it gets banned!", 1),
    ("ALERT: The new global currency system will be activated tomorrow at midnight, wiping out all bank accounts and cash values. Only those who purchase our certified gold reserves will survive the coming financial reset. Act now before it is too late!", 1),
    ("SECRET AGENDA: International leaders are planning to replace all physical currencies with microchip implants that monitor your daily activities and enforce social credit scores. The corporate media is keeping this secret to prevent mass protests!", 1),
]

# Separate features and labels
texts, labels = zip(*corpus)

# Initialize and fit TF-IDF vectorizer
vectorizer = TfidfVectorizer(max_features=2500, ngram_range=(1, 2))
X = vectorizer.fit_transform(texts)

# Train a Logistic Regression Classifier
model = LogisticRegression(C=1.0, random_state=42)
model.fit(X, labels)

# Serialize and save model artifacts
joblib.dump(model, 'model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')

print("Vectorizer ('vectorizer.pkl') and Model ('model.pkl') trained and exported successfully!")
