# OpportunityOS (NexaMind Challenge 2026 Hackathon Core)

> *"One missed opportunity can change an entire life."*
> — NexaMind 2026 Board of Innovation

OpportunityOS is a premium, AI-powered career match-vectorizer and 12-month sequence navigator. It connects students, engineers, and researchers to an active corpus of global high-status accelerators, fellowships, internships, and grants, and generates parallel-lifeline developmental projections.

---

## 🚀 How We Built It (Architecture & Logic)

OpportunityOS was built with an offline-first, hybrid double-engine architecture:

1. **Hybrid Eligibility Engine**: 
   When a user inputs their unique coordinates, the application first executes a strict, deterministic rule-based screening algorithm across our full curated opportunity database (`opportunities.csv` / `opportunities.ts`). This checks eligibility criteria including:
   - **Academic Thresholds**: Verifies minimum CGPA prerequisites.
   - **Demographics Alignment**: Screens for age limit compliance.
   - **Global Scope Guardrails**: Filters out opportunities that do not support the user's citizenship or country of operation.
   - **Keyword Relevance Vectoring**: Scores and ranks opportunities dynamically based on proximity calculations between user technical skills, listed interests, and target programs.

2. **Server-Side AI Synthesis Protocol**:
   Once the database of 30+ international accelerators, hackathons, and research grants is ranked, the top 5 match-candidates are securely packaged and passed to our Node.js Express server. Using the server-side **Google Gemini SDK**, we synthesize:
   - Deeply personalized value propositions (`whyItIsImportant`).
   - A detailed 5-year parallel projection comparing a proactive strategy (Scenario A) against passive stagnation (Scenario B).
   - An optimized 12-month sequential roadmap of tangible preparation sprints.

3. **Fallback Offline Simulator**:
   If the external Gemini connection is unreachable, a highly robust mathematical fallback simulator instantly triggers client-side, computing precise projections and structured timelines to ensure an uninterrupted, reliable UX.

---

## 🛠️ Technologies Used

- **Programming Languages**: TypeScript, Python, JavaScript, HTML5, CSS3, SQL
- **Frontend Framework**: React 19 with Vite 6
- **Server Framework**: Node.js & Express 4 (as API proxy & static file server)
- **Styling & UI Components**: Tailwind CSS v4, Framer Motion (Motion v12), Lucide React
- **Companion Local Tooling**: Streamlit & Plotly (for offline data exploration & analysis)
- **AI Models & Integrations**: Google Gemini API via `@google/genai` (Node.js SDK) & `google-genai` (Python SDK) using the `gemini-3.5-flash` model
- **Development Tooling**: esbuild (CommonJS compiler), tsx (Type stripping execution engine)

---

## 📋 Essential Input Data Parameters

To compile personalized developmental lifelines and secure match recommendations, the matching engine processes the following coordinate data:

| Parameter | Type | Purpose / Validation | Example Input |
|---|---|---|---|
| **Age** | Integer | Evaluates eligibility for restrictive youth fellowships and age-governed grants. | `21` |
| **Country** | Selection/Text | Cross-references residency boundaries and visa support constraints. | `Global` / `India` |
| **Degree Background** | Select Menu | Filters academic classifications (Bachelors, Masters, PhD, Self-taught, etc.). | `Bachelors` |
| **Current CGPA** | Decimal (0-10) | Ensures compliance with academic high-status honors filters. | `9.0` |
| **Stated Core Skills** | Comma List | Performs raw match ranking against program-focused technology tags. | `Python, TypeScript, React, SQL` |
| **Stated Focus Interests** | Comma List | Aligns user's target areas with accelerator research priorities. | `Artificial Intelligence, Social Impact` |
| **Ultimate Career Goal** | Rich Text | Deep qualitative context used by Gemini to generate application roadmaps. | *"Launch an AI-powered clinical scheduling startup."* |

---

## 🔗 Try It Out (Links & Showcases)

- **Official Live Demo Site**: [OpportunityOS Production Server](https://ais-pre-6f7zsvfg7pvwz7tfk6mixr-14264913817.asia-east1.run.app)
- **Interactive Development Server**: [Development Preview](https://ais-dev-6f7zsvfg7pvwz7tfk6mixr-14264913817.asia-east1.run.app)
- **Source Code Repository**: [GitHub Codebase](https://github.com/raguldhars1412/OpportunityOS)
- **App Store / Listing**: *Under NexaMind 2026 Core Registry*

---

## 📱 How to Run Locally (Web App)

1. **Install node dependencies**:
   ```bash
   npm install
   ```
2. **Setup your environment secrets** (create a `.env` file in root):
   ```env
   GEMINI_API_KEY="YOUR_GEMINI_KEY_HERE"
   ```
3. **Execute the full-stack server**:
   ```bash
   npm run dev
   ```
4. Find the web UI live at `http://localhost:3000`.

---

## 🐍 Streamlit Version (Local Python Offline Integration)

1. **Configure python modules**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Launch Streamlit**:
   ```bash
   streamlit run app.py
   ```
3. Explore opportunity listings offline in your browser.
