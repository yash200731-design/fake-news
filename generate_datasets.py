import pandas as pd

# Mock dataset for True/Real news (Kaggle format: title, text, subject, date)
true_data = [
    {
        "title": "Fed Keeps Interest Rates Steady Amid Growth",
        "text": "The Federal Reserve announced on Thursday that it is keeping benchmark interest rates unchanged, citing steady economic growth and moderating inflation. The central bank stated that it remains committed to its target rate and will monitor economic indicators closely in the coming months. Economists predict that the policy decision will stabilize bond markets and sustain consumer spending margins.",
        "subject": "politics",
        "date": "July 1, 2026"
    },
    {
        "title": "Researchers Release Milestone Medical Study",
        "text": "Researchers published a new peer-reviewed study on Wednesday in the Journal of Medicine detailing the impact of global trade shifts on local agricultural economies. According to the study, official reports from the agriculture department show a steady recovery in farm yields. A spokesperson stated that a press conference will be held next week to discuss long-term crop sustainability programs.",
        "subject": "worldnews",
        "date": "June 30, 2026"
    },
    {
        "title": "Highway Expansion Project Completed Ahead of Schedule",
        "text": "Local authorities confirmed that the highway expansion project has been completed ahead of schedule. The transportation department issued a statement confirming that all lanes are now open to commuter traffic, which is expected to ease congestion in the metro area. The state senate approved funding details for minor landscaping next month.",
        "subject": "politics",
        "date": "June 29, 2026"
    },
    {
        "title": "WHO Launches Initiative in Developing Nations",
        "text": "A spokesperson for the World Health Organization announced that a new initiative has been launched to combat infectious diseases in developing nations. The global program will distribute vaccines, medical supplies, and provide clinical training to local healthcare workers. Health ministers welcomed the resources as a critical step.",
        "subject": "worldnews",
        "date": "June 28, 2026"
    },
    {
        "title": "Tech Sector Earnings Report Solid Revenue Growth",
        "text": "Major tech companies reported their quarterly earnings reports, showing solid revenue growth driven by cloud computing divisions. Analysts noted that demand for database and cloud storage services remains strong across global corporate sectors. Investment firms updated their forecast metrics positively.",
        "subject": "worldnews",
        "date": "June 27, 2026"
    },
    {
        "title": "School Board Approves Budget for Academic Year",
        "text": "According to official reports, the metropolitan school board approved a new budget for the upcoming academic year. The funding will support classroom improvements, teacher salaries, and digital learning platforms across all public school districts. A spokesperson confirmed the budget was passed unanimously.",
        "subject": "politics",
        "date": "June 26, 2026"
    },
    {
        "title": "Space Agency Launches New Weather Satellite",
        "text": "The National Space Agency successfully launched a weather satellite into orbit on Tuesday evening. Mission control confirmed that the telemetry signals are healthy and the satellite has deployed its solar arrays for power collection. The system will monitor severe storm patterns in real-time.",
        "subject": "worldnews",
        "date": "June 25, 2026"
    },
    {
        "title": "Economists Urge Investments in Renewable Infrastructure",
        "text": "A panel of international economists released a statement urging governments to invest in renewable energy infrastructure. The study suggests that long-term transition policies will create jobs and stabilize global energy markets. The report was presented at the senate environment committee hearing.",
        "subject": "politics",
        "date": "June 24, 2026"
    },
    {
        "title": "City Council Passes Affordable Housing Zoning Law",
        "text": "The city council voted to approve a new zoning layout that allows for the construction of affordable housing units downtown. Municipal officials said the development plans include green spaces and pedestrian pathways. Construction is scheduled to begin in early spring.",
        "subject": "politics",
        "date": "June 23, 2026"
    },
    {
        "title": "Bilateral Trade Talks Conclude with New Agreement",
        "text": "In a press conference today, the foreign ministry declared that bilateral talks have successfully concluded, leading to a new trade agreement. The treaty is designed to lower tariffs on agricultural imports and exports. Leaders from both nations expressed confidence in mutual economic benefits.",
        "subject": "worldnews",
        "date": "June 22, 2026"
    },
    {
        "title": "Public Library to Upgrade Digital Archives",
        "text": "The municipal library board announced plans to digitize historical records dating back to the town's founding. The database project will be funded by a state history grant and is expected to take eighteen months to complete. Citizens will have free access online.",
        "subject": "worldnews",
        "date": "June 21, 2026"
    },
    {
        "title": "Forest Fire Contained in Northern Regions",
        "text": "State fire marshals announced that the forest fire in the northern national park is now eighty percent contained. Cool weather conditions and light rain have aided crews in establishing containment lines. Evacuation notices for nearby cabins were officially lifted today.",
        "subject": "worldnews",
        "date": "June 20, 2026"
    },
    {
        "title": "Transit System Introduces Contactless Payment Options",
        "text": "The metropolitan transit authority launched its new contactless fare collection system across all subway lines. Commuters can now pay for rides using credit cards or smart devices. The upgrade is expected to reduce wait times at turnstiles.",
        "subject": "politics",
        "date": "June 19, 2026"
    },
    {
        "title": "Ocean Conservation Program Receives Federal Funding",
        "text": "The environmental protection agency announced a grant of five million dollars to support marine sanctuary programs. The funds will target coral reef restoration and local plastic pollution cleanup initiatives. Research teams will start surveys next week.",
        "subject": "worldnews",
        "date": "June 18, 2026"
    },
    {
        "title": "Bilingual Education Program Expanded in Schools",
        "text": "Superintendents approved expanding bilingual immersion curricula to five more elementary campuses. The program will offer instruction in both English and Spanish to help students develop language skills. Parent-teacher associations endorsed the decision.",
        "subject": "politics",
        "date": "June 17, 2026"
    },
    {
        "title": "State Parks Announce Free Admission Weekend",
        "text": "The department of natural resources declared that admission fees will be waived for all state parks this coming weekend. The annual promotion aims to encourage families to explore hiking trails and campgrounds. Standard camping reservation fees still apply.",
        "subject": "worldnews",
        "date": "June 16, 2026"
    },
    {
        "title": "Archaeologists Discover Ancient Settlements in Southern Region",
        "text": "A team of university archaeologists unearthed pottery and stone tools estimated to be over three thousand years old. The artifacts suggest a sedentary farming community existed near the river bank. The site will be protected for further research.",
        "subject": "worldnews",
        "date": "June 15, 2026"
    },
    {
        "title": "City Hosts Annual Marathon Event in Downtown Core",
        "text": "Over ten thousand runners participated in the city's annual marathon today. Municipal police managed traffic detours around the course without incident. Organizers reported record turnout and thanked volunteers for providing water stations.",
        "subject": "worldnews",
        "date": "June 14, 2026"
    },
    {
        "title": "Small Business Grants Distributed by Commerce Department",
        "text": "The state commerce department completed its second round of distribution for local business development grants. Fifty small businesses received funding to improve storefronts and expand inventory. The governor spoke at a reception honoring recipients.",
        "subject": "politics",
        "date": "June 13, 2026"
    },
    {
        "title": "Water Treatment Facility Upgrades Online",
        "text": "Municipal engineers confirmed that the new filtration systems at the city's main water treatment facility are fully operational. The upgrade improves turbidity metrics and ensures compliance with updated federal drinking standards. Tests show clean results.",
        "subject": "worldnews",
        "date": "June 12, 2026"
    }
]

# Mock dataset for Fake News (Kaggle format: title, text, subject, date)
fake_data = [
    {
        "title": "SHOCKING TRUTH: Alien craft has landed at Secret Desert Base!",
        "text": "SHOCKING TRUTH: A secret source has confirmed that alien spacecraft have landed in a hidden desert base. The government is keeping this quiet to hide the miracle technologies which could cure all illnesses instantly. Scientists are quiet because they are being controlled by the Illuminati who want to enforce 5G radiation microchips on the entire global population. Share this before it gets taken down by the media!",
        "subject": "GovernmentSecrets",
        "date": "July 1, 2026"
    },
    {
        "title": "DOCTORS FURIOUS: Simple 24-Hour Miracle Cure Exposed!",
        "text": "MIRACLE CURE EXPOSED: Doctors are furious that this simple secret home remedy is curing cancer in just 24 hours. The pharmaceutical industry is trying to ban this organic recipe to protect their corporate profits. Click this link right now to find out the shocking recipe before they delete it forever! Do not trust chemical pills!",
        "subject": "HealthAlerts",
        "date": "June 30, 2026"
    },
    {
        "title": "MUST READ: Leaked Documents Prove the Earth is Actually Hollow!",
        "text": "MUST READ: Secret government documents leaked online prove that the earth is actually hollow and a advanced civilization lives inside it. Major media channels are refusing to report this mind-blowing discovery because they are controlled by corrupt politicians! Share this post with everyone you know immediately!",
        "subject": "LeakedTruth",
        "date": "June 29, 2026"
    },
    {
        "title": "BREAKING: Big Tech Mind Control Waves Uncovered by Whistleblower!",
        "text": "BREAKING NEWS: A massive conspiracy has been uncovered. Big tech companies are using your smart devices to project secret subliminal waves that control your thoughts and force you to buy their products. A whistleblower has escaped and revealed the whole truth in a shocking video! The media is silent!",
        "subject": "TechConspiracy",
        "date": "June 28, 2026"
    },
    {
        "title": "WARNING: Global Dictatorship Chem-Spraying Our Drinking Water!",
        "text": "WARNING: A secret chemical is being sprayed in our drinking water to make citizens submissive to a global dictatorship. Scientists who tried to warning the public have gone missing mysteriously. Buy our filtration kit today to protect your family from this hidden threat! Pass this warning on!",
        "subject": "HealthAlerts",
        "date": "June 27, 2026"
    },
    {
        "title": "SECRET SOURCE: Election Entirely Simulated by Secret Cabal!",
        "text": "ANONYMOUS SOURCE CLAIMS: The presidential election was completely simulated by supercomputers. No real votes were counted, and the results were decided months in advance by a cabal of bankers. Share this immediately before the censors wipe it from the internet! Fight the corrupt media machine!",
        "subject": "GovernmentSecrets",
        "date": "June 26, 2026"
    },
    {
        "title": "SHOCKING DISCOVERY: This Common Fruit Immunizes You Instantly!",
        "text": "SHOCKING DISCOVERY: Eating this common fruit immediately immunizes you to all types of viruses and disease. The government does not want you to know about this because they make billions from hospital visits. Reveal the secret truth by sharing this with ten friends! Cure yourself naturally!",
        "subject": "HealthAlerts",
        "date": "June 25, 2026"
    },
    {
        "title": "LEAKED VIDEO: Moon Landings Staged in Studio, Director Admits It!",
        "text": "Leaked footage shows that space agencies staged all moon landings in a television studio. The fake videos were created to win the space race. Watch this hidden video evidence showing the directors and studio setups before it gets banned by censors! Wake up people!",
        "subject": "LeakedTruth",
        "date": "June 24, 2026"
    },
    {
        "title": "ALERT: Global Currency Reset Happening Tomorrow, Cash Wiped Out!",
        "text": "ALERT: The new global currency system will be activated tomorrow at midnight, wiping out all bank accounts and cash values. Only those who purchase our certified gold reserves will survive the coming financial reset. Act now before it is too late! Protect your wealth from bankers!",
        "subject": "FinancialAlert",
        "date": "June 23, 2026"
    },
    {
        "title": "SECRET AGENDA: Microchip Implants Replacing Cash Next Month!",
        "text": "SECRET AGENDA: International leaders are planning to replace all physical currencies with microchip implants that monitor your daily activities and enforce social credit scores. The corporate media is keeping this secret to prevent mass protests! Share the truth before they implement this!",
        "subject": "GovernmentSecrets",
        "date": "June 22, 2026"
    },
    {
        "title": "REVEALED: Weather Modification Satellite Staged by Military!",
        "text": "WARNING: The weather satellite launched yesterday is actually a secret military space weapon designed to create artificial hurricanes and earthquakes. Official news sources are lying to protect this secret black project. Click here to see the coordinates of the weapon!",
        "subject": "TechConspiracy",
        "date": "June 21, 2026"
    },
    {
        "title": "CRITICAL NEWS: Hospital Admittance Rates Fake, Whistleblower Confirms!",
        "text": "A nurse who ran away from the major city hospital claims that all patient lists are entirely fabricated to scare the public. Corrupt directors are collecting federal funding bonuses for empty beds. Share this viral broadcast before it gets removed from the web!",
        "subject": "HealthAlerts",
        "date": "June 20, 2026"
    },
    {
        "title": "SECRET CORRESPONDENCE: Senate Taking Orders from Shadow Entities!",
        "text": "Leaked emails reveal that senate members are receiving orders directly from a secret underground group. No real laws are negotiated; it is all a theater play to deceive voters. Send this copy to your local representatives and demand investigations immediately!",
        "subject": "GovernmentSecrets",
        "date": "June 19, 2026"
    },
    {
        "title": "ENERGY FRAUD: Free Electricity Generator Invented, Banned by State!",
        "text": "An independent inventor created a magnet generator that provides free electricity forever. Yesterday, government agents raided his house and destroyed the plans to protect energy monopolies. Download the blueprint archive here before it gets wiped from servers!",
        "subject": "TechConspiracy",
        "date": "June 18, 2026"
    },
    {
        "title": "URGENT WARNING: Smart Meters Transmitting Harmful Radiation!",
        "text": "A new independent researcher discovered that electric smart meters project high frequency beams designed to trigger chronic headaches and sleep disorders. The utility company is hiding this evidence to avoid billions in civil lawsuits. Remove your meters today!",
        "subject": "TechConspiracy",
        "date": "June 17, 2026"
    },
    {
        "title": "EXPOSED: Clean Water Projects Actually Distributing Subliminal Pills!",
        "text": "ALERT: The clean water sanctuary grants are cover operations. They are adding microscopic tablets that dissolve slowly to calm citizen protests. Our labs ran tests and found chemical compounds. Share this shocking truth with everyone!",
        "subject": "HealthAlerts",
        "date": "June 16, 2026"
    },
    {
        "title": "THE ILLUMINATI AGENDA: Food Supply Chains Monopolized to Induce Famine!",
        "text": "A secret source says the shipping delays are artificial blockades created by the elite to trigger food shortages. They want to create a famine to reduce population counts. Save your own food supplies and buy our emergency canned packages now!",
        "subject": "GovernmentSecrets",
        "date": "June 15, 2026"
    },
    {
        "title": "SHOCKING VIDEO: Ancient Pyramids Emitting Energy Signals to Space!",
        "text": "Leaked satellite sensors show the Giza pyramids are emitting light rays to a hidden star system. Scientists are quiet because this proves alien construction. Watch the thermal scans here before it gets censored from video channels!",
        "subject": "LeakedTruth",
        "date": "June 14, 2026"
    },
    {
        "title": "URGENT: Global Banking Outage Staged to Freeze Citizen Assets!",
        "text": "The online banking error yesterday was a trial run for freezing accounts of political activists. The network failure was triggered on purpose by central banks. Move your savings into gold and offline physical assets before they freeze everything permanently!",
        "subject": "FinancialAlert",
        "date": "June 13, 2026"
    },
    {
        "title": "EXPOSED: Secret Forest Base Conducting Genetic Replications!",
        "text": "Local hikers reported seeing high security fences and armed guards near the national forest. A whistleblower states they are building cloned humans in underground bunkers. Share this post immediately to expose the horrific military research!",
        "subject": "LeakedTruth",
        "date": "June 12, 2026"
    }
]

# Write to CSV files using pandas
true_df = pd.DataFrame(true_data)
fake_df = pd.DataFrame(fake_data)

true_df.to_csv('true.csv', index=False)
fake_df.to_csv('fake.csv', index=False)

print("SUCCESS: Simulated true.csv and fake.csv datasets created successfully in Kaggle format.")
