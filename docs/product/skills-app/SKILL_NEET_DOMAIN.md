# SKILL_NEET_DOMAIN.md
# StudyOS — NEET Domain Knowledge for AI Coding Assistants
# Read this file before generating ANY study-related content, features, or UI copy

---

## WHAT THIS FILE IS FOR

Any AI assistant generating code, UI copy, prompts, or data structures for StudyOS
MUST read this file first. It contains the domain knowledge needed to:
- Write accurate chapter/topic data
- Generate correct UI labels and descriptions
- Build agent prompts that don't hallucinate NEET facts
- Handle student data with appropriate sensitivity

---

## 1. NEET EXAM STRUCTURE

```
Full name:     National Eligibility cum Entrance Test (Undergraduate)
Conducted by:  National Testing Agency (NTA)
Regulators:    National Medical Commission (NMC)
Purpose:       Admission to MBBS, BDS, AYUSH, Nursing, Veterinary colleges in India
Exam date:     First Sunday of May each year (NEET 2026 = May 3, 2026)
Mode:          Offline (pen and paper OMR sheet)
Duration:      3 hours (180 minutes)
Venue:         Centres across India (~500 cities)
Language:      13 languages (English, Hindi, Tamil, Telugu, Kannada, Malayalam,
               Marathi, Bengali, Gujarati, Odia, Punjabi, Assamese, Urdu)

STRUCTURE:
  Subject      | Questions | Marks | Negative Marking
  -------------|-----------|-------|----------------
  Physics      |    45     |  180  | -1 per wrong
  Chemistry    |    45     |  180  | -1 per wrong
  Biology      |    90     |  360  | -1 per wrong
  TOTAL        |   180     |  720  | +4 correct, -1 wrong, 0 unattempted

SCORING:
  Correct answer:    +4 marks
  Wrong answer:      -1 mark
  Unattempted:        0 marks
  Maximum marks:    720/720
  NEET 2025 cut-off (General):  ~720–137 (qualifying); ~600+ for good government college

SUBJECT WEIGHTAGE (% of total marks):
  Biology:   360/720 = 50%  ← MOST IMPORTANT
  Physics:   180/720 = 25%
  Chemistry: 180/720 = 25%
```

---

## 2. CHAPTER TIER SYSTEM

```
Tier 1 — HIGH YIELD (must-do before any other chapter)
  Definition: Chapters that consistently produce 5+ questions in NEET papers
  Physics Tier 1:   Current Electricity, Electrostatics, Capacitance, Magnetism,
                    EMI, Alternating Current, Ray Optics, Wave Optics, Modern Physics
                    (Atoms, Nuclei, Dual Nature), Semiconductors, Rotational Motion
  Chemistry Tier 1: Chemical Bonding, Coordination Compounds, d-Block, p-Block (Cl2, XII),
                    Equilibrium, Electrochemistry, Aldehydes/Ketones/Acids, Hydrocarbons,
                    Haloalkanes, Alcohols/Phenols/Ethers, Nitrogen Compounds
  Biology Tier 1:   Molecular Basis of Inheritance, Biotechnology Principles,
                    Principles of Inheritance, Evolution, Sexual Reproduction in
                    Flowering Plants, Human Reproduction, Reproductive Health,
                    Human Health & Disease, Biotechnology Applications, Photosynthesis,
                    Respiration, Cell Biology, Body Fluids & Circulation, Excretion

Tier 2 — IMPORTANT (do after Tier 1 is solid)
  Definition: 2–4 questions per paper, consistent

Tier 3 — COMPLETE BUT DON'T OVER-INVEST
  Definition: 0–2 questions per paper, less consistent
```

---

## 3. DELETED TOPICS (2023–24 NMC RATIONALIZATION — PERMANENT)

These topics are REMOVED from NEET. Never include them in:
- Quiz questions
- Study checklists
- Roadmap planning
- Any feature that suggests "topics to study"

```
CHEMISTRY DELETED:
  - Solid State (crystal systems, packing efficiency, Bragg's equation, defects)
  - Surface Chemistry (adsorption isotherms, colloids, emulsions, gold number)
  - Metallurgy (thermodynamic extraction, electrochemical extraction, refining methods)
  - Hydrogen (isotopes, physical/chemical properties of H2, hydrides, water chemistry)
  - s-Block Elements (Li, Na, K, Mg, Ca — preparation and properties chapter)
  - Environmental Chemistry (air pollutants, water pollution, Green Chemistry)
  - Chemistry in Everyday Life (drugs, cleansing agents, food preservatives)
  - Polymers (addition, condensation, copolymers, rubber, Bakelite)

PHYSICS DELETED:
  - Rolling motion detailed calculations (rolling without slipping, rolling on incline)
  - Compound pendulum
  - Poisson's ratio
  - Detailed derivation of displacement current
  - Davisson-Germer experiment (experimental details removed; concept retained)

BIOLOGY DELETED:
  - Detailed ecological succession (concept retained, not detailed stages)
  - Aquaculture details in Strategies for Enhancement in Food Production
  - Detailed historical classification systems (pre-5 kingdom)
  - Numerical pollution standards in Environmental Issues
```

---

## 4. STUDY STRATEGY RULES (for AI agents)

```
NCERT FIRST RULE:
  Biology:   ~90% of NEET Biology questions are directly from NCERT
  Chemistry: ~70% Inorganic/Organic from NCERT; numerical from solved examples
  Physics:   ~60% from NCERT concepts; ~40% application/numerical
  
  AI agents MUST cite NCERT source. Never give answers without "NCERT Class X, Chapter Y"

SUBJECT TIME ALLOCATION:
  Recommended: Biology 50%, Chemistry 25%, Physics 25%
  Biology has most marks AND is most NCERT-direct → highest ROI
  Common mistake: students give equal time to all three → sub-optimal

CHAPTER PRIORITY ORDER (if exam < 8 weeks):
  1. All Tier 1 incomplete chapters first
  2. Tier 2 chapters where student has < 50% completion
  3. Tier 1 revision (chapters done but not revised in 7+ days)
  4. Tier 2 completion
  5. Tier 3 only if time permits

REVISION FREQUENCY RULES:
  Tier 1 chapters: revise every 7 days minimum
  Tier 2 chapters: revise every 14 days
  Tier 3 chapters: one revision before exam is sufficient
  
COMMON MISTAKE PATTERNS (real student errors — agents should warn about these):
  Physics:
    - Sign convention errors in optics (mirror formula vs lens formula)
    - Forgetting negative sign in Bohr energy levels
    - Using wrong formula for parallel vs series combination
    - Confusing induced EMF direction (Lenz's law vs right-hand rule)
  Chemistry:
    - Confusing Kc and Kp; forgetting Δn in Kp = Kc(RT)^Δn
    - Wrong oxidation states for Cr and Mn in compounds
    - Confusing SN1 vs SN2 conditions
    - Forgetting to check for geometric isomerism in coordination complexes
    - Writing wrong products for Aldol (self vs mixed)
  Biology:
    - Confusing meiosis I prophase sub-stages (Leptotene→Zygotene→Pachytene→Diplotene→Diakinesis)
    - Confusing syngamy and triple fusion in double fertilization
    - Mixing up Bt toxin target insects (Cry1Ac = Lepidoptera, not all insects)
    - Forgetting Meselson-Stahl used ¹⁵N not ¹⁴C
    - Confusing lac operon induction by allolactose (not lactose itself)
```

---

## 5. INDIAN STUDENT CONTEXT

```
COACHING CULTURE:
  - 70%+ NEET students attend coaching (Allen, Aakash, FIITJEE, PW, Vedantu, local)
  - Students often have both school + coaching notes → confusing duplication
  - Coaching institutes number chapters differently from NCERT
  - StudyOS uses NCERT chapter numbering as canonical

CLASS TYPES:
  - Class 11 (Fresher): studying NEET alongside school for first time
  - Class 12 (Senior): final year school + NEET preparation simultaneously
  - Dropper: completed Class 12, preparing full-time for NEET repeat
  - Droppers typically have more time but more pressure

STUDY PATTERNS:
  - Most students study 8–12 hours/day during dropper year
  - Peak study: 6 AM–10 AM and 3 PM–10 PM
  - WhatsApp is primary communication for study groups
  - Most study on smartphone + paper notes (not laptop)

GEOGRAPHY:
  - 60%+ NEET aspirants from: Tamil Nadu, UP, Rajasthan, Maharashtra, Kerala, AP/Telangana
  - Significant number from Bihar, MP, Karnataka, Gujarat
  - Many students from small towns with limited English fluency
  - Tamil Nadu has unique NEET counseling (state quota vs All India quota)

PRESSURE & MENTAL HEALTH:
  - NEET is one of most competitive exams in the world (2M+ applicants, 90k+ seats)
  - Student suicide linked to NEET failure is a documented issue in India
  - AI tone MUST be:
    ✅ Encouraging, supportive, realistic
    ✅ Focused on progress not rank comparison
    ✅ Acknowledging effort not just outcomes
    ❌ Never pressure-based ("you MUST score X or else")
    ❌ Never dismissive of difficulty ("it's easy, just study more")
    ❌ Never rank-focused in casual conversation
  - If student shows signs of extreme stress, AI should gently suggest:
    "Preparing for NEET is tough — it's okay to take breaks. If you're feeling
    overwhelmed, talking to a trusted adult or counselor can really help."
```

---

## 6. NEET BIOLOGY — KEY DIAGRAMS (AI must reference correctly)

```
Diagrams that NEET tests directly (must be in study materials):
  - Z-scheme of photosynthesis (cyclic + non-cyclic photophosphorylation)
  - Calvin cycle (C3 pathway): labeled steps with RuBisCO, 3-PGA, G3P, RuBP
  - Krebs cycle: substrates, products, cofactors at each step
  - Structure of a nephron (PCT, loop of Henle, DCT, CD, vasa recta)
  - Structure of human heart (4 chambers, valves, vessels)
  - Polygonum type embryo sac (8-nucleate, 7-celled, labeled)
  - Spermatogenesis and oogenesis parallel diagrams
  - DNA double helix (B-form, measurements: 3.4Å, 34Å, 10bp/turn)
  - lac operon (operator, promoter, structural genes, repressor binding)
  - Structure of antibody (2 heavy + 2 light chains, Fab, Fc, disulfide bonds)
  - Plasmodium life cycle (liver stage + RBC stage)
  - Ecological pyramids (numbers, biomass, energy) — which can be inverted
  - Mitosis and meiosis stages (prophase, metaphase, anaphase, telophase)
  - Meiosis I prophase sub-stages (leptotene to diakinesis)
```

---

## 7. NEET CHEMISTRY — KEY NAMED REACTIONS (AI must know all)

```
Must-know named reactions (frequently tested in NEET):
  Aldol condensation      — two aldehydes/ketones with α-H → β-hydroxy carbonyl
  Cannizzaro reaction     — aldehydes WITHOUT α-H → disproportionation
  Clemmensen reduction    — C=O → CH2 using Zn-Hg/HCl
  Wolff-Kishner reduction — C=O → CH2 using NH2NH2/KOH
  Markovnikov's rule      — H adds to C with more H in HX addition to alkenes
  Anti-Markovnikov        — H adds to C with fewer H (peroxide effect)
  SN1                     — 1 step, carbocation intermediate, racemization
  SN2                     — 2 step, backside attack, inversion (Walden)
  Sandmeyer reaction      — ArN2+ + CuCl/CuBr → ArCl/ArBr
  Balz-Schiemann          — ArN2+ + HBF4 → ArF
  Gabriel synthesis       — phthalimide → primary amine (no secondary/tertiary)
  Hofmann bromamide       — amide → primary amine (chain shortens by 1 C)
  Reimer-Tiemann          — phenol + CHCl3/NaOH → ortho-hydroxybenzaldehyde
  Kolbe's reaction        — phenol + CO2/NaOH → salicylic acid
  Rosenmund reduction     — acid chloride → aldehyde (H2/Pd-BaSO4)
  Stephen's reduction     — nitrile → aldehyde (SnCl2/HCl)
  Hell-Volhard-Zelinsky   — carboxylic acid + Br2/PCl3 → α-bromo acid
  Gattermann-Koch         — benzene + CO + HCl/AlCl3 → benzaldehyde
  Williamson synthesis    — alkoxide + primary alkyl halide → ether (SN2)
  Aldol condensation      — between two carbonyl compounds with α-H
  Wurtz reaction          — 2 RX + 2Na → R-R + 2NaX (only for same R)
```

---

## 8. DATA STRUCTURES FOR SYLLABUS (how to model in code)

```typescript
// Canonical chapter structure
interface Chapter {
  id: string;                    // "bio_ch24" format
  number: number;                // NCERT chapter number
  name: string;                  // Official NCERT chapter name
  subject: "Physics" | "Chemistry" | "Biology";
  class: 11 | 12;
  tier: 1 | 2 | 3;
  weightage_pct: number;         // Approximate % of total NEET marks
  is_deleted: boolean;           // True if removed in 2023 rationalization
  deleted_reason?: string;       // "NMC rationalization 2023-24"
  topics: Topic[];
}

interface Topic {
  id: string;
  name: string;
  is_high_yield: boolean;        // True if frequently directly tested
  subtopics: Subtopic[];
}

interface Subtopic {
  id: string;
  name: string;
  definition: string;            // 1-2 sentence NCERT-aligned definition
  is_high_yield: boolean;
  is_deleted: boolean;
  difficulty: "easy" | "medium" | "hard";
  ncert_page_ref?: string;       // e.g., "NCERT Class 12 Biology, p.163"
  common_mistakes?: string[];    // What students typically get wrong here
}

// Chapter numbering reference (NCERT)
// Physics Class 11: Ch 1-10 (Kinematics → Oscillations)
// Physics Class 12: Ch 1-14 (Electric Charges → Semiconductors) = 11-30 in app
// Chemistry Class 11: Ch 1-14
// Chemistry Class 12: Ch 1-16 (but 8 chapters deleted)
// Biology Class 11: Ch 1-22
// Biology Class 12: Ch 1-16
```

---

## 9. NEET SCORE BENCHMARKS (for rank predictor feature)

```
Score Range  | Approx AIR (General) | Likely College Type
-------------|---------------------|--------------------
700–720      | 1–100               | AIIMS Delhi, top government colleges
680–699      | 100–1,000           | AIIMS (other), top state medical colleges
650–679      | 1,000–5,000         | Good government medical colleges (state)
620–649      | 5,000–15,000        | Government medical colleges (most states)
580–619      | 15,000–40,000       | Government colleges (some states), private
550–579      | 40,000–80,000       | Mostly private colleges
500–549      | 80,000–1,50,000     | Private colleges
450–499      | 1,50,000–3,00,000   | Some private colleges
< 450        | 3,00,000+           | Below most college cut-offs

CATEGORY ADJUSTMENTS (approximate):
  OBC-NCL:  reduce score by ~30–40 for equivalent AIR
  SC:       reduce score by ~80–100 for equivalent AIR
  ST:       reduce score by ~100–120 for equivalent AIR
  EWS:      reduce score by ~20–30 for equivalent AIR

QUALIFYING CUT-OFF (to be eligible for counseling):
  General:          720–137 (50th percentile)
  OBC/SC/ST:        136–107 (40th percentile)
  PwBD General:     136–121 (45th percentile)

DISCLAIMER always show:
  "These are estimates based on historical data. Actual cut-offs change
  every year based on paper difficulty, number of candidates, and
  seat matrix. Always verify with official NTA/MCC data."
```

---

## 10. AI RESPONSE QUALITY RULES FOR NEET CONTENT

```
ALWAYS:
  ✅ Cite NCERT: "According to NCERT Class 12 Biology, Chapter 6..."
  ✅ Use exam-relevant language (match how NEET phrases questions)
  ✅ Give the "exam trick" version AND the conceptual understanding
  ✅ Flag high-yield points: "⭐ This is directly asked in NEET 3–4 times"
  ✅ Warn about deleted topics: "❌ Note: Solid State was removed from NEET syllabus in 2023"
  ✅ Use Indian units and context (Indian examples in chemistry problems)
  ✅ For numerical physics: show step-by-step with units at each step
  ✅ For biology diagrams: describe what to draw and label, in order

NEVER:
  ❌ Generate quiz questions from deleted topics
  ❌ Contradict NCERT (even if technically more accurate — NEET tests NCERT)
  ❌ Use advanced concepts not in NEET syllabus (e.g., quantum field theory)
  ❌ Give probability/prediction without appropriate disclaimer
  ❌ Use competitive/ranking language that adds pressure
  ❌ Say "this is easy" — everything is hard for someone
  ❌ Recommend skipping any Tier 1 chapter regardless of time pressure
  ❌ Answer questions about topics from completely different subjects
     (student asking Physics AI about Biology should be redirected)
```

---

*SKILL_NEET_DOMAIN.md — StudyOS Enterprise | May 2026*
*Read before: generating quiz questions, writing study content, building roadmap agents,*
*writing UI copy for study features, designing checklist data structures*
