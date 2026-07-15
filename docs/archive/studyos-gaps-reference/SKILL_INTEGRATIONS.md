# SKILL_INTEGRATIONS.md
# StudyOS — Complete Integration Guide
# How to connect Claude + Gemini + NotebookLM + Notion + GitHub + WhatsApp
# Read before building any integration or MCP connection

---

## 1. CLAUDE API INTEGRATION (Primary AI)

```typescript
// src/lib/claude-client.ts
import Anthropic from '@anthropic-ai/sdk';
import { getApiKey } from './key-store';

export async function askClaude({
  userMessage,
  chapterContext,
  conversationHistory = [],
  stream = true,
}: {
  userMessage: string;
  chapterContext?: { name: string; subject: string; topics: string[] };
  conversationHistory?: { role: 'user' | 'assistant'; content: string }[];
  stream?: boolean;
}) {
  const apiKey = await getApiKey('anthropic');
  if (!apiKey) throw new Error('No Claude API key configured. Add it in Settings.');

  const client = new Anthropic({ apiKey, dangerouslyAllowBrowser: true });

  const systemPrompt = `You are an expert NEET 2026 AI tutor.
${chapterContext ? `Current chapter: ${chapterContext.subject} — ${chapterContext.name}
Topics in this chapter: ${chapterContext.topics.join(', ')}` : ''}

Rules:
- Answer ONLY within NEET 2026 syllabus scope
- Explain at NEET depth — not too basic, not too advanced
- Always cite NCERT when possible: [NCERT Class X Y, Ch Z, p.NNN]
- Use Indian English and relatable examples
- For formulas: show formula → define each variable → give units → show example
- For Biology: exact NCERT lines matter — quote them when relevant
- End every explanation with 1 checkpoint question to test understanding`;

  const messages = [
    ...conversationHistory,
    { role: 'user' as const, content: userMessage },
  ];

  if (stream) {
    return client.messages.stream({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1500,
      system: systemPrompt,
      messages,
    });
  }

  return client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 1500,
    system: systemPrompt,
    messages,
  });
}
```

### Claude with Notion MCP (read student's notes)
```typescript
// When Claude needs to read Notion workspace
const response = await fetch('https://api.anthropic.com/v1/messages', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 1000,
    system: 'You are a NEET 2026 study coach. Read the student\'s Notion workspace and give personalized advice.',
    messages: [{ role: 'user', content: userQuery }],
    mcp_servers: [{
      type: 'url',
      url: 'https://mcp.notion.com/mcp',
      name: 'notion-mcp',
    }],
  }),
});
```

### Claude with Google Drive MCP
```typescript
const response = await fetch('https://api.anthropic.com/v1/messages', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 1000,
    messages: [{ role: 'user', content: 'Find my NEET formula charts in Drive and summarize the Physics formulas' }],
    mcp_servers: [{
      type: 'url',
      url: 'https://drivemcp.googleapis.com/mcp/v1',
      name: 'google-drive',
    }],
  }),
});
```

---

## 2. GEMINI API (Vision + Drive access)

```typescript
// src/lib/gemini-client.ts
// Use Gemini for: image questions, Drive file reading, diagram OCR

import { GoogleGenerativeAI } from '@google/generative-ai';
import { getApiKey } from './key-store';

export async function askGeminiWithImage({
  imageBase64,
  mimeType,
  question,
}: {
  imageBase64: string;
  mimeType: 'image/jpeg' | 'image/png' | 'image/webp';
  question: string;
}) {
  const apiKey = await getApiKey('google');
  if (!apiKey) throw new Error('No Gemini API key. Add it in Settings.');

  const genAI = new GoogleGenerativeAI(apiKey);
  const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

  const result = await model.generateContent([
    {
      inlineData: { mimeType, data: imageBase64 },
    },
    `You are a NEET 2026 expert. ${question}
     If this is a textbook page: identify the chapter and explain the concept shown.
     If this is a diagram: label all parts and explain their functions in NEET context.
     If this is a handwritten note: extract the topics and map them to NEET syllabus.`,
  ]);

  return result.response.text();
}

// Route image questions to Gemini, text questions to Claude
export function routeQuestion(question: string, hasImage: boolean) {
  if (hasImage) return 'gemini';
  if (question.length < 50) return 'groq';    // fast for simple questions
  return 'claude';                              // complex reasoning → Claude
}
```

---

## 3. GROQ API (Fast free inference)

```typescript
// src/lib/groq-client.ts
// Use Groq for: quick questions, quiz generation, simple explanations
// Model: llama-3.3-70b (fastest, free tier available)

export async function askGroq(messages: { role: string; content: string }[]) {
  const apiKey = await getApiKey('groq');
  
  const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'llama-3.3-70b-versatile',
      messages,
      max_tokens: 1000,
      temperature: 0.3,
      stream: true,
    }),
  });

  return response.body; // ReadableStream for streaming
}
```

---

## 4. LLM ROUTER (Central dispatcher)

```typescript
// src/lib/llm-router.ts
// ALWAYS use this — never call providers directly from components

type Provider = 'claude' | 'gemini' | 'groq' | 'ollama';
type TaskType = 'explain' | 'quiz_gen' | 'roadmap' | 'image_ocr' | 'motivation' | 'pyq_analysis';

const ROUTING_TABLE: Record<TaskType, Provider> = {
  explain:      'claude',    // accurate NCERT-grounded explanations
  quiz_gen:     'groq',      // fast MCQ generation
  roadmap:      'claude',    // complex structured planning
  image_ocr:    'gemini',    // vision capability
  motivation:   'groq',      // fast, simple
  pyq_analysis: 'claude',    // deep analysis
};

export async function routeToLLM({
  task,
  messages,
  image,
  chapterContext,
}: {
  task: TaskType;
  messages: { role: string; content: string }[];
  image?: { base64: string; mimeType: string };
  chapterContext?: object;
}) {
  const provider = ROUTING_TABLE[task];
  
  // Check if preferred provider has key configured
  const hasKey = await getApiKey(provider);
  const actualProvider = hasKey ? provider : await getFallbackProvider();

  switch (actualProvider) {
    case 'claude':
      return askClaude({ userMessage: messages.at(-1)!.content, chapterContext, conversationHistory: messages.slice(0, -1) });
    case 'gemini':
      if (image) return askGeminiWithImage({ ...image, question: messages.at(-1)!.content });
      return askGeminiText(messages);
    case 'groq':
      return askGroq(messages);
    default:
      throw new Error('No AI provider configured. Add an API key in Settings.');
  }
}

async function getFallbackProvider(): Promise<Provider> {
  // Try in order: groq (free) → claude → gemini → error
  for (const p of ['groq', 'claude', 'gemini'] as Provider[]) {
    if (await getApiKey(p)) return p;
  }
  throw new Error('No AI provider configured');
}
```

---

## 5. API KEY STORE (Dexie.js — device-only)

```typescript
// src/lib/key-store.ts
// CRITICAL: Keys NEVER leave the device. Never send to Supabase.

import Dexie from 'dexie';

interface KeyRecord {
  provider: string;
  encryptedKey: string;
  addedAt: Date;
}

class KeyDatabase extends Dexie {
  keys!: Dexie.Table<KeyRecord, string>;
  constructor() {
    super('StudyOSKeys');
    this.version(1).stores({ keys: 'provider, encryptedKey, addedAt' });
  }
}

const db = new KeyDatabase();

// Simple obfuscation (not true encryption — for privacy, not security)
// Keys are on device anyway, user can see them in Settings
function obfuscate(key: string): string {
  return btoa(key.split('').reverse().join(''));
}
function deobfuscate(encoded: string): string {
  return atob(encoded).split('').reverse().join('');
}

export async function saveApiKey(provider: string, key: string) {
  await db.keys.put({ provider, encryptedKey: obfuscate(key), addedAt: new Date() });
}

export async function getApiKey(provider: string): Promise<string | null> {
  const record = await db.keys.get(provider);
  if (!record) return null;
  return deobfuscate(record.encryptedKey);
}

export async function removeApiKey(provider: string) {
  await db.keys.delete(provider);
}

export async function testApiKey(provider: string, key: string): Promise<boolean> {
  try {
    switch (provider) {
      case 'anthropic':
        const r = await fetch('https://api.anthropic.com/v1/messages', {
          method: 'POST',
          headers: { 'x-api-key': key, 'anthropic-version': '2023-06-01', 'Content-Type': 'application/json' },
          body: JSON.stringify({ model: 'claude-haiku-4-5-20251001', max_tokens: 10, messages: [{ role: 'user', content: 'Hi' }] }),
        });
        return r.ok;
      case 'groq':
        const gr = await fetch('https://api.groq.com/openai/v1/models', {
          headers: { 'Authorization': `Bearer ${key}` },
        });
        return gr.ok;
      case 'google':
        const ge = await fetch(`https://generativelanguage.googleapis.com/v1/models?key=${key}`);
        return ge.ok;
      default:
        return false;
    }
  } catch { return false; }
}
```

---

## 6. NOTEBOOKLM INTEGRATION

NotebookLM doesn't have a public API yet. Use these workarounds:

### Workaround 1 — Export summaries as context
```typescript
// When student exports NotebookLM summaries as markdown:
// They paste the markdown into the app → stored as a note → used as RAG context

async function addNotebookLMExport(markdownContent: string, chapterId: string) {
  await supabase.from('notes').insert({
    user_id: userId,
    chapter_id: chapterId,
    title: 'NotebookLM Summary',
    content_md: markdownContent,
    source_type: 'ai_generated',
  });
  // Now Claude can access this via note RAG
}
```

### Workaround 2 — NotebookLM export guide (show in app)
```
In-app guide: "How to use NotebookLM with StudyOS"
1. Open your NotebookLM: https://notebooklm.google.com/notebook/37462bcc...
2. Ask: "Summarize [chapter name] in NEET exam format"
3. Copy the response
4. In StudyOS → Notes → Add Note → Paste
5. StudyOS AI can now reference this content in your chat sessions
```

### Workaround 3 — Podcast transcript import
```
NotebookLM audio transcript → paste into Notes → Claude references it
Especially useful for Biology diagrams (audio explanation → text context)
```

---

## 7. NOTION MCP INTEGRATION

```typescript
// Using Notion MCP in Claude API calls from the app
// (requires user to have Notion connected in Claude.ai)

// For the StudyOS app, use Notion API directly:
// src/lib/notion-client.ts

export async function syncMistakeToNotion(mistake: {
  question: string;
  wrongAnswer: string;
  correctAnswer: string;
  chapter: string;
  errorType: string;
}) {
  const notionApiKey = await getApiKey('notion');
  const mistakeDbId = localStorage.getItem('notion_mistake_db_id');
  
  if (!notionApiKey || !mistakeDbId) return; // Notion not configured

  await fetch('https://api.notion.com/v1/pages', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${notionApiKey}`,
      'Notion-Version': '2022-06-28',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      parent: { database_id: mistakeDbId },
      properties: {
        'Question Summary': { title: [{ text: { content: mistake.question.slice(0, 100) } }] },
        'Date': { date: { start: new Date().toISOString().split('T')[0] } },
        'Chapter': { rich_text: [{ text: { content: mistake.chapter } }] },
        'My Wrong Answer': { rich_text: [{ text: { content: mistake.wrongAnswer } }] },
        'Correct Answer': { rich_text: [{ text: { content: mistake.correctAnswer } }] },
        'Error Type': { select: { name: mistake.errorType } },
        'Resolved': { checkbox: false },
      },
    }),
  });
}

// Sync chapter completion to Notion progress tracker
export async function syncChapterCompletion(chapterName: string, subject: string) {
  const notionApiKey = await getApiKey('notion');
  const progressDbId = localStorage.getItem('notion_progress_db_id');
  if (!notionApiKey || !progressDbId) return;

  // Find existing page for chapter
  const searchResult = await fetch(`https://api.notion.com/v1/databases/${progressDbId}/query`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${notionApiKey}`,
      'Notion-Version': '2022-06-28',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      filter: {
        property: 'Chapter Name',
        title: { equals: chapterName },
      },
    }),
  });

  const data = await searchResult.json();
  const pageId = data.results[0]?.id;

  if (pageId) {
    // Update existing page
    await fetch(`https://api.notion.com/v1/pages/${pageId}`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${notionApiKey}`,
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        properties: {
          'Status': { select: { name: '🟢 Completed' } },
          'Last Studied': { date: { start: new Date().toISOString().split('T')[0] } },
        },
      }),
    });
  }
}
```

---

## 8. GITHUB INTEGRATION

```typescript
// src/lib/github-client.ts
// Access PW study materials from rohitkumarnaidu/NEET-NOTES

const REPO_OWNER = 'rohitkumarnaidu';
const REPO_NAME = 'NEET-NOTES';
const BASE_URL = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}`;

export async function getRepoFolders() {
  const response = await fetch(`${BASE_URL}/contents`);
  return response.json();
  // Returns: BOARDS PYQ, CHAPTERWISE PYQ, FORMULA CHARTS, MIND MAPS,
  //          NCERT CHAPTER WISE, NEET PYQ, SHORT NOTE
}

export async function getFilesInFolder(folderName: string) {
  const encodedName = encodeURIComponent(folderName);
  const response = await fetch(`${BASE_URL}/contents/${encodedName}`);
  return response.json();
}

export async function getFileDownloadUrl(filePath: string): Promise<string> {
  const response = await fetch(`${BASE_URL}/contents/${encodeURIComponent(filePath)}`);
  const data = await response.json();
  return data.download_url; // Direct download link
}

// In Chapter Detail page: show related PW PDF
export async function findRelatedPDF(chapterName: string) {
  const files = await getFilesInFolder('NCERT CHAPTER WISE');
  // Match file name to chapter
  const match = files.find((f: any) =>
    f.name.toLowerCase().includes(chapterName.toLowerCase().split(' ')[0])
  );
  return match ? match.download_url : null;
}
```

---

## 9. YOUTUBE INTEGRATION

```typescript
// src/lib/youtube-client.ts
// Find PW lecture videos for each chapter

const YOUTUBE_API_KEY = import.meta.env.VITE_YOUTUBE_API_KEY;

export async function findLectureVideos(chapterName: string, subject: string) {
  const query = `Physics Wallah ${subject} ${chapterName} NEET 2026`;
  
  const response = await fetch(
    `https://www.googleapis.com/youtube/v3/search?` +
    `part=snippet&q=${encodeURIComponent(query)}&type=video&maxResults=5&key=${YOUTUBE_API_KEY}`
  );
  
  const data = await response.json();
  
  return data.items.map((item: any) => ({
    videoId: item.id.videoId,
    title: item.snippet.title,
    thumbnail: item.snippet.thumbnails.medium.url,
    channelName: item.snippet.channelTitle,
    url: `https://youtube.com/watch?v=${item.id.videoId}`,
  }));
}

// Filter for trusted channels only
export function filterTrustedChannels(videos: any[]) {
  const TRUSTED = ['Physics Wallah', 'Unacademy NEET', 'Vedantu NEET', 'Aakash NEET'];
  return videos.filter(v => TRUSTED.some(t => v.channelName.includes(t)));
}
```

---

## 10. WHATSAPP INTEGRATION (Twilio)

```typescript
// Set up in Supabase Edge Function (whatsapp-scheduler)
// Students opt-in by providing their phone number in Settings

// Message templates (pre-approved by Meta for WhatsApp Business):

const TEMPLATES = {
  daily_reminder: (name: string, chapter: string, daysLeft: number) =>
    `🌅 Good morning, ${name}!\n\n📚 Today: ${chapter}\n⏳ ${daysLeft} days to NEET 2026\n\nOpen StudyOS → studyos.app\n\nYou've got this! 💪`,

  milestone: (name: string, milestone: string) =>
    `🎉 Amazing, ${name}!\n\n${milestone}\n\nKeep this momentum going!\n📱 studyos.app`,

  weekly_report: (name: string, chaptersThisWeek: number, avgScore: number) =>
    `📊 Your Week in Review, ${name}!\n\n✅ Chapters completed: ${chaptersThisWeek}\n📈 Avg quiz score: ${avgScore}%\n\nFull report → studyos.app/analytics`,

  spaced_repetition: (name: string, chapter: string) =>
    `🔄 Time to revise!\n\n${name}, it's been 7 days since you studied ${chapter}.\n\nQuick 10-min revision now → studyos.app`,
};
```

---

## 11. ENVIRONMENT SETUP CHECKLIST

```bash
# 1. Clone and setup
git clone https://github.com/rohitkumarnaidu/NEET-NOTES  # PW notes
# Create new repo: github.com/[you]/studyos for the app

# 2. Supabase setup
npx supabase init
npx supabase start
npx supabase db push  # runs all migrations

# 3. Vercel deploy
npx vercel --prod

# 4. Secrets (Supabase Edge Functions)
npx supabase secrets set ANTHROPIC_API_KEY=sk-ant-xxx
npx supabase secrets set TWILIO_ACCOUNT_SID=ACxxx
npx supabase secrets set RAZORPAY_KEY_SECRET=xxx

# 5. Student API keys (set in app Settings — stored in browser only)
# Claude API: https://console.anthropic.com
# Groq API (FREE): https://console.groq.com  ← Recommend this for sister
# Gemini API (FREE tier): https://aistudio.google.com

# 6. Notion setup
# Get API key: https://www.notion.so/my-integrations
# Add integration to NEET workspace
# Copy database IDs from URL

# 7. NotebookLM
# Already set up: https://notebooklm.google.com/notebook/37462bcc...
# Add syllabus MD as additional source
```

---

## 12. INTEGRATION PRIORITY ORDER

```
Build in this exact order:

WEEK 1 (Sister can use immediately):
1. Claude API → AI chat in Chapter pages ← MOST IMPORTANT
2. Groq API → fast quiz generation (free, no cost to sister)
3. Supabase → save progress + quiz scores

WEEK 2:
4. Gemini API → camera/photo question answering
5. Notion API → sync mistakes + chapter completions to Notion
6. GitHub API → show related PW PDFs in chapter pages

WEEK 3:
7. YouTube API → related lecture videos per chapter
8. WhatsApp → daily study reminders
9. Razorpay → payments (if opening to other students)

WEEK 4+:
10. NotebookLM export flow → when API becomes available
11. Full mock test with OMR UI
12. PWA push notifications
```
