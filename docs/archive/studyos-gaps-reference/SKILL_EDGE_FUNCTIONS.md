# SKILL_EDGE_FUNCTIONS.md
# StudyOS — Supabase Edge Functions (Deno + TypeScript)
# Read before writing any serverless function

---

## 1. STANDARD EDGE FUNCTION TEMPLATE

```typescript
// supabase/functions/_shared/cors.ts
export const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

// supabase/functions/[function-name]/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import { corsHeaders } from '../_shared/cors.ts';

serve(async (req: Request) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    // Auth: get user from JWT
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) throw new Error('Missing authorization header');

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_ANON_KEY')!,
      { global: { headers: { Authorization: authHeader } } }
    );

    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) throw new Error('Unauthorized');

    // Parse body
    const body = await req.json();

    // ... your logic here ...
    const result = {};

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 200,
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: error.message === 'Unauthorized' ? 401 : 500,
    });
  }
});
```

---

## 2. ALL EDGE FUNCTIONS TO BUILD

### Function 1: roadmap-generator
```typescript
// supabase/functions/roadmap-generator/index.ts
// Generates personalized weekly study plan using Claude API

import Anthropic from 'https://esm.sh/@anthropic-ai/sdk@0.27.0';

interface RoadmapRequest {
  examDate: string;        // ISO date
  studyHoursPerDay: number;
  completedChapters: string[];   // chapter IDs
  weakChapters: string[];        // chapter IDs with low confidence
  targetScore: number;           // 550, 600, 650, 700
}

serve(async (req) => {
  // ... auth setup ...

  const body: RoadmapRequest = await req.json();
  const weeksRemaining = Math.floor(
    (new Date(body.examDate).getTime() - Date.now()) / (7 * 24 * 60 * 60 * 1000)
  );

  // Fetch all chapters from DB
  const { data: chapters } = await supabase
    .from('chapters')
    .select('*, subjects(name)')
    .eq('deleted', false)
    .order('tier', { ascending: true });

  const pendingChapters = chapters.filter(c =>
    !body.completedChapters.includes(c.id)
  );

  const anthropic = new Anthropic({
    apiKey: Deno.env.get('ANTHROPIC_API_KEY')!,
  });

  const prompt = `You are a NEET 2026 expert planner.
Generate a ${weeksRemaining}-week study roadmap.

STUDENT PROFILE:
- Study hours/day: ${body.studyHoursPerDay}
- Weeks remaining: ${weeksRemaining}
- Target score: ${body.targetScore}/720
- Pending chapters (${pendingChapters.length}):
${pendingChapters.map(c => `  - ${c.subjects.name}: ${c.name} [Tier ${c.tier}, ${c.weightage_pct}% weightage]`).join('\n')}
- Weak chapters (prioritize revision): ${body.weakChapters.join(', ')}

OUTPUT: Valid JSON only. No markdown. No explanation.
Schema:
{
  "weeks": [
    {
      "weekNumber": 1,
      "theme": "string (e.g. Genetics Marathon 🧬)",
      "aiTip": "string (max 100 chars)",
      "items": [
        {
          "chapterId": "uuid",
          "dayOfWeek": 1,
          "hoursPlanned": 2.5,
          "itemType": "study|revision|quiz"
        }
      ]
    }
  ]
}

Rules:
- Tier 1 chapters first
- Biology gets 50% of time (it's 50% of NEET)
- Last 2 weeks: only revision + full mocks
- Max 3 new chapters per week
- Include 1 quiz day per week per subject`;

  const response = await anthropic.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 4000,
    messages: [{ role: 'user', content: prompt }],
  });

  const roadmapData = JSON.parse(response.content[0].text);

  // Save to DB
  const { data: roadmap } = await supabase
    .from('roadmaps')
    .insert({
      user_id: user.id,
      exam_date: body.examDate,
      total_weeks: weeksRemaining,
      ai_model: 'claude-sonnet-4-20250514',
    })
    .select()
    .single();

  // Insert weeks + items in batch
  for (const week of roadmapData.weeks) {
    const { data: weekRow } = await supabase
      .from('roadmap_weeks')
      .insert({ roadmap_id: roadmap.id, week_number: week.weekNumber, theme: week.theme, ai_tip: week.aiTip })
      .select().single();

    await supabase.from('roadmap_items').insert(
      week.items.map(item => ({ week_id: weekRow.id, ...item }))
    );
  }

  return new Response(JSON.stringify({ roadmapId: roadmap.id, weeks: roadmapData.weeks }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  });
});
```

### Function 2: quiz-generator
```typescript
// supabase/functions/quiz-generator/index.ts
// Generates NEET-style MCQs using Claude API

interface QuizRequest {
  chapterId: string;
  topicIds?: string[];
  questionCount: number;   // 5-180
  difficulty: 'easy' | 'medium' | 'hard' | 'mixed';
  quizType: 'chapter' | 'topic' | 'weak_area' | 'full_mock';
  includePYQ: boolean;
}

// ... standard setup ...
const body: QuizRequest = await req.json();

// Fetch chapter + topics
const { data: chapter } = await supabase
  .from('chapters')
  .select('*, subjects(name), topics(*)')
  .eq('id', body.chapterId)
  .single();

// Check if PYQ available
let pyqQuestions = [];
if (body.includePYQ) {
  const { data: pyqs } = await supabase
    .from('questions')
    .select('*')
    .eq('chapter_id', body.chapterId)
    .eq('source', 'pyq')
    .limit(Math.floor(body.questionCount * 0.4));
  pyqQuestions = pyqs || [];
}

const aiQuestionsNeeded = body.questionCount - pyqQuestions.length;

const anthropic = new Anthropic({ apiKey: Deno.env.get('ANTHROPIC_API_KEY')! });

const prompt = `You are an NTA NEET paper setter.
Generate ${aiQuestionsNeeded} NEET-style MCQs.

Chapter: ${chapter.subjects.name} — ${chapter.name}
Difficulty: ${body.difficulty}
Topics: ${chapter.topics.map(t => t.name).join(', ')}

RULES:
1. Each question tests exactly one concept
2. All 4 options must be plausible (no obviously wrong options)
3. Exactly one correct answer
4. Match actual NEET question language and style
5. Include trap questions (is_trap: true) — 20% of questions
6. Difficulty distribution for 'mixed': 30% easy, 50% medium, 20% hard

OUTPUT: Valid JSON array only. No markdown.
[
  {
    "stem": "question text",
    "optionA": "...", "optionB": "...", "optionC": "...", "optionD": "...",
    "correctOption": "A|B|C|D",
    "explanation": "2-3 line clear explanation of why answer is correct and why other options are wrong",
    "difficulty": "easy|medium|hard",
    "isTrap": false,
    "topicHint": "which sub-topic this tests"
  }
]`;

const response = await anthropic.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 4000,
  messages: [{ role: 'user', content: prompt }],
});

const aiQuestions = JSON.parse(response.content[0].text);

// Save AI questions to DB
const { data: savedQuestions } = await supabase
  .from('questions')
  .insert(aiQuestions.map(q => ({
    chapter_id: body.chapterId,
    stem: q.stem,
    option_a: q.optionA, option_b: q.optionB,
    option_c: q.optionC, option_d: q.optionD,
    correct_option: q.correctOption,
    explanation: q.explanation,
    difficulty: q.difficulty,
    source: 'ai_generated',
    is_trap: q.isTrap,
  })))
  .select();

// Shuffle and return combined questions
const allQuestions = [...pyqQuestions, ...savedQuestions]
  .sort(() => Math.random() - 0.5);

return new Response(JSON.stringify({ questions: allQuestions }), {
  headers: { ...corsHeaders, 'Content-Type': 'application/json' },
});
```

### Function 3: note-extractor
```typescript
// supabase/functions/note-extractor/index.ts
// OCR + AI topic extraction from uploaded notes

interface ExtractRequest {
  noteId: string;
  ocrText: string;    // already processed by client-side Tesseract.js
}

// ... standard setup ...

const anthropic = new Anthropic({ apiKey: Deno.env.get('ANTHROPIC_API_KEY')! });

const { data: allChapters } = await supabase
  .from('chapters')
  .select('id, name, subjects(name), topics(id, name)')
  .eq('deleted', false);

const prompt = `You are a NEET syllabus expert.
Analyze this student's handwritten/typed notes and map them to the NEET 2026 syllabus.

NOTES TEXT:
"""
${body.ocrText}
"""

AVAILABLE CHAPTERS:
${allChapters.map(c => `- ${c.subjects.name}: ${c.name} (id: ${c.id})`).join('\n')}

OUTPUT: Valid JSON only. No markdown.
{
  "primaryChapter": { "id": "uuid", "confidence": 0.0-1.0 },
  "additionalChapters": [{ "id": "uuid", "confidence": 0.0-1.0 }],
  "extractedTopics": [
    { "text": "extracted topic text", "chapterId": "uuid", "confidence": 0.0-1.0 }
  ],
  "gaps": ["topic in notes not found in NEET syllabus"],
  "quality": { "score": 0.0-1.0, "issues": ["blurry text", "incomplete notes"] },
  "summary": "2-line summary of what this note covers"
}`;

const response = await anthropic.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 2000,
  messages: [{ role: 'user', content: prompt }],
});

const extraction = JSON.parse(response.content[0].text);

// Update note with extraction results
await supabase.from('notes').update({
  chapter_id: extraction.primaryChapter?.id,
  extraction_done: true,
}).eq('id', body.noteId);

// Save extractions
if (extraction.extractedTopics?.length > 0) {
  await supabase.from('note_extractions').insert(
    extraction.extractedTopics.map(t => ({
      note_id: body.noteId,
      chapter_id: t.chapterId,
      extracted_text: t.text,
      confidence: t.confidence,
    }))
  );
}

return new Response(JSON.stringify(extraction), {
  headers: { ...corsHeaders, 'Content-Type': 'application/json' },
});
```

### Function 4: whatsapp-scheduler
```typescript
// supabase/functions/whatsapp-scheduler/index.ts
// Called by pg_cron daily at 6 AM IST — sends WhatsApp study reminders

import { Twilio } from 'https://esm.sh/twilio@4.19.0';

// This function is called by a CRON trigger, not by users
// Set up: in Supabase Dashboard → Database → Extensions → pg_cron
// select cron.schedule('daily-whatsapp', '30 0 * * *', $$
//   select net.http_post(url := 'https://[project].supabase.co/functions/v1/whatsapp-scheduler',
//     headers := '{"Authorization": "Bearer [service_role_key]"}')
// $$);

const supabaseAdmin = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
);

// Get all active users with phone numbers
const { data: users } = await supabaseAdmin
  .from('profiles')
  .select('id, full_name, phone, streak_count, exam_date')
  .not('phone', 'is', null)
  .gte('last_active', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString());

const twilio = new Twilio(
  Deno.env.get('TWILIO_ACCOUNT_SID')!,
  Deno.env.get('TWILIO_AUTH_TOKEN')!
);

for (const user of users) {
  const daysLeft = Math.floor(
    (new Date(user.exam_date).getTime() - Date.now()) / (24 * 60 * 60 * 1000)
  );

  // Get today's roadmap item for this user
  const { data: todayItem } = await supabaseAdmin
    .from('roadmap_items')
    .select('chapters(name, subjects(name))')
    .eq('roadmap_weeks.roadmap.user_id', user.id)
    .eq('day_of_week', new Date().getDay() || 7)
    .eq('completed', false)
    .limit(1)
    .single();

  const chapterName = todayItem?.chapters?.name || 'your weak areas';
  const subject = todayItem?.chapters?.subjects?.name || '';

  const message = `🌅 Good morning, ${user.full_name.split(' ')[0]}!

📚 Today: ${subject ? `${subject} — ` : ''}${chapterName}
🔥 Streak: ${user.streak_count} days
⏳ NEET in: ${daysLeft} days

Open StudyOS → [studyos.app]

Keep going! 💪`;

  try {
    await twilio.messages.create({
      from: `whatsapp:${Deno.env.get('TWILIO_WHATSAPP_NUMBER')}`,
      to: `whatsapp:+91${user.phone}`,
      body: message,
    });
  } catch (e) {
    console.error(`Failed to send to ${user.id}: ${e.message}`);
  }
}
```

### Function 5: razorpay-webhook
```typescript
// supabase/functions/razorpay-webhook/index.ts
// Handles Razorpay payment webhooks to update user plans

import crypto from 'https://deno.land/std@0.168.0/node/crypto.ts';

// Verify Razorpay webhook signature
function verifySignature(body: string, signature: string, secret: string): boolean {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(body)
    .digest('hex');
  return expectedSignature === signature;
}

const rawBody = await req.text();
const signature = req.headers.get('x-razorpay-signature') || '';
const secret = Deno.env.get('RAZORPAY_WEBHOOK_SECRET')!;

if (!verifySignature(rawBody, signature, secret)) {
  return new Response('Invalid signature', { status: 400 });
}

const event = JSON.parse(rawBody);

const supabaseAdmin = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
);

if (event.event === 'subscription.activated') {
  const sub = event.payload.subscription.entity;
  const notes = sub.notes; // userId stored in notes during payment creation

  await supabaseAdmin.from('subscriptions').upsert({
    user_id: notes.userId,
    plan: notes.plan,
    status: 'active',
    razorpay_sub_id: sub.id,
    amount_paise: sub.amount,
    expires_at: new Date(sub.end_at * 1000).toISOString(),
  });

  await supabaseAdmin.from('profiles').update({
    plan: 'pro',
    plan_expires: new Date(sub.end_at * 1000).toISOString(),
  }).eq('id', notes.userId);
}

if (event.event === 'subscription.cancelled') {
  await supabaseAdmin.from('subscriptions')
    .update({ status: 'cancelled', cancelled_at: new Date().toISOString() })
    .eq('razorpay_sub_id', event.payload.subscription.entity.id);

  await supabaseAdmin.from('profiles')
    .update({ plan: 'free' })
    .eq('id', event.payload.subscription.entity.notes?.userId);
}

return new Response('OK', { status: 200 });
```

---

## 3. LOCAL DEVELOPMENT

```bash
# Install Supabase CLI
npm install -g supabase

# Start local Supabase
supabase start

# Serve functions locally
supabase functions serve --env-file .env.local

# Test a function
curl -i --location --request POST 'http://localhost:54321/functions/v1/quiz-generator' \
  --header 'Authorization: Bearer [anon-key]' \
  --header 'Content-Type: application/json' \
  --data '{"chapterId":"uuid","questionCount":10,"difficulty":"mixed","quizType":"chapter","includePYQ":true}'

# Deploy function
supabase functions deploy quiz-generator

# Set secrets
supabase secrets set ANTHROPIC_API_KEY=sk-ant-xxx
supabase secrets set TWILIO_ACCOUNT_SID=ACxxx
supabase secrets set RAZORPAY_WEBHOOK_SECRET=xxx
```

---

## 4. ENV VARIABLES REQUIRED

```bash
# .env.local (never commit to git)
VITE_SUPABASE_URL=https://[project].supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...

# Supabase Edge Function secrets (set via CLI)
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_WHATSAPP_NUMBER=+14155238886
RAZORPAY_KEY_ID=rzp_xxx
RAZORPAY_KEY_SECRET=xxx
RAZORPAY_WEBHOOK_SECRET=xxx
POSTHOG_API_KEY=phc_xxx
```
