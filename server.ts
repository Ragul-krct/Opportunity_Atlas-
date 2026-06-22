import express from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import { GoogleGenAI } from '@google/genai';
import dotenv from 'dotenv';
import { OPPORTUNITIES, Opportunity } from './src/data/opportunities';

// Configure dotenv
dotenv.config();

const app = express();
app.use(express.json());

// Lazy-initialize Gemini Client
let geminiClient: any = null;
function getGeminiClient() {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey || apiKey === "MY_GEMINI_API_KEY" || apiKey.trim() === "") {
    return null;
  }
  if (!geminiClient) {
    geminiClient = new GoogleGenAI({
      apiKey: apiKey,
      httpOptions: {
        headers: {
          'User-Agent': 'aistudio-build',
        }
      }
    });
  }
  return geminiClient;
}

// ---------------------- MATCHING & SYNTHESIS API ----------------------
app.post('/api/synthesize', async (req, res) => {
  try {
    const { age, country, degree, cgpa, skills, interests, careerGoal } = req.body;

    if (!age || !country || !degree || cgpa === undefined) {
      return res.status(400).json({ error: "Missing required profile parameters." });
    }

    // Standard scoring logic for ranking the opportunities
    const userSkills = (skills || "").toLowerCase().split(',').map((s: string) => s.trim()).filter(Boolean);
    const userInterests = (interests || "").toLowerCase().split(',').map((i: string) => i.trim()).filter(Boolean);
    const userGoal = (careerGoal || "").toLowerCase();

    const scoredOpportunities = OPPORTUNITIES.map((opp) => {
      let score = 0;

      // 1. Core eligibility guards
      const degreeMatches = opp.eligibleDegrees.includes("Any") || 
        opp.eligibleDegrees.some(d => d.toLowerCase() === degree.toLowerCase());
      
      const countryMatches = opp.eligibleCountries.includes("Global") || 
        opp.eligibleCountries.some(c => c.toLowerCase() === country.toLowerCase());

      const ageMatches = age >= opp.minAge && age <= opp.maxAge;
      const cgpaMatches = cgpa >= opp.minimumCGPA;

      if (!degreeMatches) score -= 3;
      if (!countryMatches) score -= 4;
      if (!ageMatches) score -= 5;
      if (!cgpaMatches) score -= 6;

      // 2. Keyword matching weights
      opp.primarySkills.forEach(skill => {
        if (userSkills.some(us => us.includes(skill.toLowerCase()) || skill.toLowerCase().includes(us))) {
          score += 4;
        }
      });

      opp.interests.forEach(interest => {
        if (userInterests.some(ui => ui.includes(interest.toLowerCase()) || interest.toLowerCase().includes(ui))) {
          score += 5;
        }
      });

      // Match career goal contents
      const lowerDesc = opp.description.toLowerCase();
      const lowerName = opp.name.toLowerCase();
      userInterests.forEach(ui => {
        if (lowerDesc.includes(ui) || lowerName.includes(ui)) {
          score += 2;
        }
      });

      if (userGoal) {
        opp.interests.forEach(interest => {
          if (userGoal.includes(interest.toLowerCase())) score += 3;
        });
      }

      // Add a small priority bonus
      if (opp.priorityLevel === "Critical") score += 2;
      else if (opp.priorityLevel === "High") score += 1;

      return { opp, score };
    });

    // Sort opportunities by descending score and take the top 5
    scoredOpportunities.sort((a, b) => b.score - a.score);
    const top5 = scoredOpportunities.slice(0, 5).map(item => item.opp);

    const clientAI = getGeminiClient();
    
    if (clientAI) {
      // ---------------- AI ACTIVE GENERATION MODE ----------------
      const prompt = `
You are OpportunityOS, an elite AI-fueled career navigator and global hackathon judge in the NexaMind Challenge 2026.
Analyze this user profile:
- Age: ${age}
- Country of citizenship: ${country}
- Selected Degree background: ${degree}
- Current CGPA: ${cgpa}/10.0
- Stated Core Skills: ${skills}
- Stated Focus Interests: ${interests}
- Ultimate Career Goal: "${careerGoal}"

We have filtered our primary challenge dataset containing 30+ international fellowships, hackathons, and accelerators down to these top 5 curated matches:
${JSON.stringify(top5, null, 2)}

Provide a highly personalized synthesis. You MUST return a single valid JSON object containing exactly three fields:

1. "personalized_opportunities": An array of exactly 5 objects. Each object represents one of the matched opportunities from the listed array above. Keep the exact 'name', 'category', 'provider', 'priorityLevel', 'actionToTake', and 'description' keys from the matched item.
   BUT, you must generate a new and deeply personalized string key "whyItIsImportant" (2-3 concise, high-intensity sentences) describing exactly how this opportunity acts as a game-changer for their specific career goal (${careerGoal}), showing them how to bridge their current skills (${skills}) and interests (${interests}) into immediate professional leverage.

2. "comparison_scenarios": An object detailing Scenario A and Scenario B to build parallel lifelines:
   - "scenario_a": Represents immediate pro-active implementation.
   - "scenario_b": Represents standard classroom inertia.
   For each scenario, you must output exactly five dimensions: "skillGrowth", "portfolioGrowth", "networkingGrowth", "careerGrowth", and "learningGrowth".
   For each dimension, output:
     - "score": A precise integer between 10 and 100.
     - "desc": A brief, highly tailored impact snippet of 1 sentence showing the direct consequence.

3. "one_year_roadmap": An array of exactly 12 month items ("Month 1" to "Month 12"). Each item must contain:
   - "month": "Month 1" through "Month 12"
   - "goal": Month objective (custom tailored to their skills & opportunity application timelines)
   - "action": Specific, actionable next steps to prepare, apply, or build portfolios
   - "expectedOutcome": A concrete, measurable checkpoint they achieve by end of month.

IMPORTANT GUIDELINES:
- Output your reply ONLY as a valid JSON string. Do NOT add markdown code blocks (such as \`\`\`json or \`\`\`), no text outside the JSON structure, and no preamble or postamble.
- Ensure all quotes are escaped properly and syntax is 100% parseable by JSON.parse.
`;

      try {
        const aiResponse = await clientAI.models.generateContent({
          model: 'gemini-3.5-flash',
          contents: prompt
        });

        const rawText = aiResponse.text || '';
        let cleanText = rawText.trim();
        // Discard markdown blocks if the model insists on using them
        if (cleanText.startsWith('```json')) {
          cleanText = cleanText.substring(7);
        } else if (cleanText.startsWith('```')) {
          cleanText = cleanText.substring(3);
        }
        if (cleanText.endsWith('```')) {
          cleanText = cleanText.substring(0, cleanText.length - 3);
        }
        cleanText = cleanText.trim();

        const result = JSON.parse(cleanText);
        return res.json(result);
      } catch (e: any) {
        console.error("Gemini API call or JSON parsing failed. Falling back to local synthesis.", e);
        // Fall back to rule-based fallback if Gemini has issues
      }
    }

    // ---------------- DETERMINISTIC LOCAL SYNTHESIS MODE (FALLBACK) ----------------
    // This executes if no API key is provided, or if the API key fails to resolve.
    const personalizedOpps = top5.map(opp => {
      return {
        ...opp,
        whyItIsImportant: `This is the perfect match for you since it directly aligns with your listed skills in ${skills}. Participating allows you to showcase the caliber of your talents directly to ${opp.provider || 'top-tier platforms'} and validates your goal of "${careerGoal}".`
      };
    });

    const comparisonScenarios = {
      scenario_a: {
        skillGrowth: { score: 95, desc: "Rapidly apply your skills in a high-intensity professional environment." },
        portfolioGrowth: { score: 90, desc: "A prestigious project added to your portfolio, complete with external peer validations." },
        networkingGrowth: { score: 85, desc: "Establish direct working connections with international fellows, industry judges, and experts." },
        careerGrowth: { score: 92, desc: "Differentiate yourself from millions of conventional textbook candidates instantly." },
        learningGrowth: { score: 98, desc: "Accelerate learning via feedback loops, real deadlines, and expert recommendations." }
      },
      scenario_b: {
        skillGrowth: { score: 40, desc: "Basic classroom assignments that lack original problem statement exposure." },
        portfolioGrowth: { score: 12, desc: "No original flagship projects, making you heavily reliant on standard dry CV listings." },
        networkingGrowth: { score: 10, desc: "Limited entirely to your immediate university peers and local friends." },
        careerGrowth: { score: 20, desc: "Competing on basic standards, highly susceptible to automated background screening pools." },
        learningGrowth: { score: 35, desc: "Stagnant, linear learning curve dominated by rote exam memorization rather than building." }
      }
    };

    const oneYearRoadmap = Array.from({ length: 12 }, (_, index) => {
      const monthNum = index + 1;
      let goal = "Acquiring Materials & Setup";
      let action = `Research application cycles for matched opportunities. Set up clear workspace structures and select developer environments.`;
      let outcome = "Perfect documentation set and early checklist setup.";

      if (monthNum === 2) {
        goal = "Deep Alignment Work";
        action = `Analyze winning repositories and award profiles. Reach out to advisors or previous challenge winners.`;
        outcome = "Actionable checklist of past winners' secrets.";
      } else if (monthNum === 3) {
        goal = "Core Skills Acceleration";
        action = `Create micro-projects practicing your core technical stacks: ${skills}. Build minor functional features.`;
        outcome = "2 live mini-modules published publicly on GitHub.";
      } else if (monthNum === 4) {
        goal = "Logical Prototyping Phase";
        action = `Convert your career goal concepts into an elegant design mock, detailing user interactions.`;
        outcome = "Completed Figma flow drafts and user journey mappings.";
      } else if (monthNum === 5) {
        goal = "MVP Build Sprint #1";
        action = `Develop the core algorithm or core utility engine. Test all database and API layers intensely.`;
        outcome = "Functional local backend routing with high reliability logs.";
      } else if (monthNum === 6) {
        goal = "Frontend Integration Sprint #2";
        action = `Integrate clean user interactive panels, charts, responsive views and high-vibe CSS themes.`;
        outcome = "Fully integrated pre-alpha prototype running locally.";
      } else if (monthNum === 7) {
        goal = "Beta Launch & Direct Feedback";
        action = `Release early version to close colleagues or local developer boards. Note critical bugs immediately.`;
        outcome = "Detailed log of early feedback items and 5 bug fixes.";
      } else if (monthNum === 8) {
        goal = "Polishing and Deploying";
        action = `Publish repository online with standard README documentation, clear license keys, and setup guides.`;
        outcome = "One-click deployment link live on public platforms.";
      } else if (monthNum === 9) {
        goal = "Application Submission Phase";
        action = `Draft personal statements, structure CV, record 3-minute video presentation showing live demo.`;
        outcome = "Perfected document templates prepared for matching grants.";
      } else if (monthNum === 10) {
        goal = "Live Pitch and Community Audits";
        action = `Participate in Q&A rounds, reach out to selection committee, and schedule mentoring sessions.`;
        outcome = "High-quality response materials ready for judge inquiries.";
      } else if (monthNum === 11) {
        goal = "Networking Alignment Scaling";
        action = `Connect with other participants on LinkedIn and Discord. Join community-wide study groups.`;
        outcome = "Addition of 20+ premium peers inside your professional network.";
      } else if (monthNum === 12) {
        goal = "Vector Review and Goal Realization";
        action = `Evaluate metrics achieved over the year. Scale prototype further or finalize entry loops.`;
        outcome = "Achievement of active fellowship match or accelerator invitations.";
      }

      return {
        month: `Month ${monthNum}`,
        goal,
        action,
        expectedOutcome: outcome
      };
    });

    return res.json({
      personalized_opportunities: personalizedOpps,
      comparison_scenarios: comparisonScenarios,
      one_year_roadmap: oneYearRoadmap
    });

  } catch (error: any) {
    console.error("Unhandled endpoint error:", error);
    res.status(500).json({ error: "Internal server error occurred.", details: error.message });
  }
});

// Serve frontend assets
const isProd = process.env.NODE_ENV === 'production';
const root = process.cwd();

async function startServer() {
  if (!isProd) {
    // Integrate Vite development server middleware
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'custom',
    });
    
    app.use(vite.middlewares);
    
    app.use('*', async (req, res, next) => {
      const url = req.originalUrl;
      try {
        let template = await vite.transformIndexHtml(url, `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>OpportunityOS | NexaMind Challenge 2026</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>`);
        res.status(200).set({ 'Content-Type': 'text/html' }).end(template);
      } catch (e) {
        vite.ssrFixStacktrace(e as Error);
        next(e);
      }
    });

  } else {
    // Production build delivery
    app.use(express.static(path.join(root, 'dist')));
    app.get('*', (req, res) => {
      res.sendFile(path.join(root, 'dist', 'index.html'));
    });
  }

  const port = process.env.PORT || 3000;
  app.listen(port, () => {
    console.log(`OpportunityOS server running perfectly on http://localhost:${port}`);
  });
}

startServer();
