# SKILL_DESIGN.md
# StudyOS — Design System Reference for AI Coding Assistants
# Read this file before generating ANY UI component, page, or styling for StudyOS

---

## 1. COLOR TOKENS

### Brand Colors
```css
--color-brand-50:  #EEF2FF
--color-brand-100: #E0E7FF
--color-brand-200: #C7D2FE
--color-brand-300: #A5B4FC
--color-brand-400: #818CF8
--color-brand-500: #6366F1
--color-brand-600: #4F46E5   ← PRIMARY (buttons, links, active state)
--color-brand-700: #4338CA
--color-brand-800: #3730A3
--color-brand-900: #312E81
--color-brand-950: #1E1B4B   ← DARK backgrounds
```

### Subject Colors (STRICT — always use for subject-related UI)
```css
/* Physics = Blue */
--color-physics-light: #DBEAFE
--color-physics:       #3B82F6
--color-physics-dark:  #1D4ED8

/* Chemistry = Violet */
--color-chemistry-light: #EDE9FE
--color-chemistry:       #8B5CF6
--color-chemistry-dark:  #6D28D9

/* Biology = Emerald */
--color-biology-light: #D1FAE5
--color-biology:       #10B981
--color-biology-dark:  #047857
```

### Tier Colors (priority indicators)
```css
--color-tier1: #EF4444   /* Red — Tier 1 high priority */
--color-tier2: #F59E0B   /* Amber — Tier 2 medium */
--color-tier3: #9CA3AF   /* Gray — Tier 3 low */
```

### Semantic Colors
```css
--color-success:  #10B981  /* Green */
--color-warning:  #F59E0B  /* Amber */
--color-danger:   #EF4444  /* Red */
--color-info:     #3B82F6  /* Blue */
```

### Neutral Palette (Slate)
```css
--color-neutral-50:  #F8FAFC   /* Page background (light) */
--color-neutral-100: #F1F5F9
--color-neutral-200: #E2E8F0   /* Borders */
--color-neutral-300: #CBD5E1
--color-neutral-400: #94A3B8   /* Placeholder text */
--color-neutral-500: #64748B   /* Secondary text */
--color-neutral-600: #475569
--color-neutral-700: #334155   /* Primary text (dark mode) */
--color-neutral-800: #1E293B   /* Card bg (dark mode) */
--color-neutral-900: #0F172A   /* Page bg (dark mode) */
--color-neutral-950: #020617
```

---

## 2. TYPOGRAPHY

### Fonts
```
Primary:    Inter (latin — all UI text)
Tamil:      Noto Sans Tamil (when Tamil language selected)
Hindi:      Noto Sans Devanagari (when Hindi language selected)
Mono:       JetBrains Mono (code blocks, formulas in code context)
Math:       KaTeX (rendered math: E=mc², ΔG=-RTlnK)
```

### Scale
```
text-xs:   12px / line-height: 1.5
text-sm:   14px / line-height: 1.5
text-base: 16px / line-height: 1.5  ← body text default
text-lg:   18px / line-height: 1.625
text-xl:   20px / line-height: 1.5
text-2xl:  24px / line-height: 1.333
text-3xl:  30px / line-height: 1.25
text-4xl:  36px / line-height: 1.111
text-5xl:  48px / line-height: 1
```

### Weight Rules
```
font-normal   (400): body text, descriptions
font-medium   (500): labels, UI text
font-semibold (600): headings H3-H4, chapter names
font-bold     (700): headings H1-H2, stats, scores
```

### DO / DON'T
```
✅ DO: Use text-sm for subtopic definitions (preserve screen space on mobile)
✅ DO: Use font-semibold for chapter names in lists
✅ DO: Use text-2xl font-bold for the score/progress number in StatCards
❌ DON'T: Use text-xs for anything interactive (too small to tap)
❌ DON'T: Mix font weights within a single label
❌ DON'T: Use font-black (900) — too heavy, not in design system
```

---

## 3. SPACING SYSTEM

All spacing is multiples of 4px (Tailwind 4px base):
```
p-1  = 4px    (tight internal padding)
p-2  = 8px    (small component padding)
p-3  = 12px
p-4  = 16px   (standard component padding)
p-5  = 20px
p-6  = 24px   (card padding)
p-8  = 32px   (section padding)
p-10 = 40px
p-12 = 48px   (page section padding)
p-16 = 64px   (page top/bottom)
```

### Gap Rules
```
gap-2 = 8px    (between tight items like badges)
gap-3 = 12px   (between list items)
gap-4 = 16px   (standard gap)
gap-6 = 24px   (between sections)
gap-8 = 32px   (between major sections)
```

---

## 4. BORDER RADIUS RULES

```
rounded-sm   = 4px   (small UI elements: badges, tags)
rounded      = 6px   (inputs, buttons)
rounded-md   = 8px   (most cards, modals inner)
rounded-lg   = 12px  (cards, panels)
rounded-xl   = 16px  (bottom sheets, large cards)
rounded-2xl  = 24px  (feature cards, modals)
rounded-full = 9999px (avatars, progress pills, icon buttons)
```

### DO / DON'T
```
✅ DO: rounded-lg for ChapterCard, NoteCard, StatCard
✅ DO: rounded-full for Avatar, ProgressRing container, badge counts
✅ DO: rounded for Button, Input, Select
❌ DON'T: Use rounded-none (sharp corners) except for dividers/separators
❌ DON'T: Mix different radius values within the same component family
```

---

## 5. SHADOW SYSTEM

```css
shadow-sm:  0 1px 2px 0 rgb(0 0 0 / 0.05)       (subtle, inputs)
shadow:     0 1px 3px 0 rgb(0 0 0 / 0.1)          (cards)
shadow-md:  0 4px 6px -1px rgb(0 0 0 / 0.1)       (dropdowns, tooltips)
shadow-lg:  0 10px 15px -3px rgb(0 0 0 / 0.1)     (modals, panels)
shadow-xl:  0 20px 25px -5px rgb(0 0 0 / 0.1)     (bottom sheets)
shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25)   (dialogs)
```

---

## 6. COMPONENT SPECIFICATIONS

### Button
```tsx
// Variants:
// primary  — brand-600 bg, white text (main CTAs)
// secondary — brand-100 bg, brand-700 text (secondary actions)
// ghost   — transparent bg, brand-600 text (tertiary actions)
// destructive — danger bg, white text (delete, remove)
// outline — border + brand text (alternative to ghost)

// Sizes:
// sm: h-8, px-3, text-sm   (compact contexts)
// md: h-10, px-4, text-sm  (DEFAULT)
// lg: h-12, px-6, text-base (important CTAs)
// icon: h-10, w-10          (icon-only buttons)

// MOBILE MINIMUM: 44×44px tap target (use p-2 on icon buttons)
// LOADING: show spinner + disable (never just disable without feedback)
// DISABLED: opacity-50, cursor-not-allowed, pointer-events-none

✅ <Button variant="primary" size="lg">Build My Roadmap</Button>
✅ <Button variant="ghost" size="sm"><ChevronRight /></Button>
❌ <button className="bg-indigo-600 text-white px-4 py-2">...</button>  // Use component
❌ <Button disabled> (without loading state explanation to user)
```

### Input
```tsx
// Always include: label, error state, helper text slot
// Height: h-10 (40px) — never smaller (mobile tap)
// Focus ring: ring-2 ring-brand-500 ring-offset-1
// Error state: border-danger, error message in text-danger text-sm below
// Password: show/hide toggle button inside input

✅ <Input label="Your Name" placeholder="Enter your name" error={errors.name} />
❌ <input className="border rounded px-3 py-2" />  // raw HTML input
```

### Checkbox
```tsx
// Size: 18×18px minimum (mobile tap = wrapper must be 44px)
// States: unchecked (border), checked (brand-600 fill + white check), indeterminate (dash)
// High-yield variant: adds ⭐ star icon after label
// Deleted variant: strikethrough label + opacity-50 + ❌ badge
// ALWAYS: pair with visible label (never checkbox alone)

✅ <SubtopicCheckbox subtopic={s} onComplete={handleComplete} />
❌ <input type="checkbox" /> // Raw HTML
```

### Badge
```tsx
// Subject badges: Physics (blue bg), Chemistry (violet bg), Biology (emerald bg)
// Tier badges: Tier 1 (red), Tier 2 (amber), Tier 3 (gray)
// Status: complete (green), in-progress (blue), not-started (gray), deleted (red strikethrough)
// Size: always text-xs, px-2, py-0.5, rounded-full or rounded-sm

✅ <SubjectBadge subject="Biology" />  // emerald colored
✅ <TierBadge tier={1} />              // red "Tier 1" badge
❌ <span className="bg-green-500 text-white rounded px-2">Biology</span> // hardcoded
```

### ProgressRing (SVG)
```tsx
// Animated SVG circle, clockwise fill from top (12 o'clock)
// Center: show percentage number, text-lg font-bold
// Subject-colored: Physics=blue, Chemistry=violet, Biology=emerald
// Sizes: sm(48px), md(80px), lg(120px), xl(160px)
// Animation: 300ms ease-in-out on value change, CSS stroke-dashoffset transition

✅ <ProgressRing value={68} subject="Biology" size="lg" label="Biology" />
❌ Horizontal progress bar for subject completion (use ring instead)
```

### ChapterCard
```tsx
// Shows: chapter name (font-semibold), subject badge, tier badge,
//        weightage (X%), progress bar, last studied date
// Tap action: navigate to chapter detail
// Height: auto (min h-20 on mobile)
// States: not-started (gray border), in-progress (brand border), complete (green border + ✅)
// Swipe right (mobile): mark all complete
// Long press: options menu (mark complete, skip, view in NotebookLM)
```

### SubtopicItem
```tsx
// Layout: [checkbox] [name + definition] [badges] [timestamp]
// Name: text-sm font-medium
// Definition: text-xs text-neutral-500, max 2 lines (expandable on tap)
// Badges: ⭐ (high yield), ❌ (deleted), difficulty pill
// Completed: name gets line-through, text-neutral-400, bg-neutral-50/dark:bg-neutral-800/50
// Minimum height: 44px (tap target)
// Optimistic update: check immediately, sync in background
```

---

## 7. LAYOUT RULES

### Mobile-first (MANDATORY)
```
All CSS written for mobile FIRST, then override for larger screens:
  default styles = 375px mobile
  sm: (640px+) = small tablets
  md: (768px+) = tablet landscape / small laptop
  lg: (1024px+) = desktop
  xl: (1280px+) = large desktop

NEVER write desktop-first (no "hide on mobile" approach)
```

### App Shell
```
Mobile:
  - Full screen content
  - BottomNav fixed at bottom (5 tabs: Dashboard/Syllabus/AI/Notes/Profile)
  - TopBar: logo + chapter title + notification bell
  - Content: scrollable, padded pb-20 (above bottom nav)

Desktop (lg:):
  - SideNav: 240px fixed left panel (collapsible to 64px icon-only)
  - Content area: flex-1, overflow-y-auto
  - No BottomNav on desktop
  - TopBar still present (search + user menu)
```

### Safe Areas (mobile)
```
// Always account for iOS safe areas and Android navigation bar
padding-bottom: env(safe-area-inset-bottom)
padding-top: env(safe-area-inset-top)
// Use Tailwind v4 (CSS-first config): pb-safe, pt-safe via @utility in globals.css
```

---

## 8. DARK MODE

```
Strategy: class-based dark mode (add 'dark' to html element)
Storage: localStorage('theme') → 'dark' | 'light' | 'system'
Default: 'dark' (students study at night — dark first)

Color mappings:
  Background:    bg-neutral-50     → dark:bg-neutral-900
  Surface/Card:  bg-white          → dark:bg-neutral-800
  Border:        border-neutral-200 → dark:border-neutral-700
  Text primary:  text-neutral-900   → dark:text-neutral-50
  Text secondary: text-neutral-500  → dark:text-neutral-400
  Text muted:    text-neutral-400   → dark:text-neutral-600
  Brand:         bg-brand-600       → dark:bg-brand-500 (slightly lighter)

RULE: Every component must have explicit dark: variants. No "it looks fine" without checking.
TOOL: Use browser DevTools dark mode emulation to verify every component.
```

---

## 9. ANIMATION RULES

### Performance-safe animations ONLY
```css
/* ✅ Use: opacity, transform — GPU-accelerated */
.fade-in { animation: fadeIn 150ms ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

/* ✅ Use: transition on specific properties */
.progress-bar { transition: width 300ms ease-in-out; }
.ring-fill { transition: stroke-dashoffset 300ms ease-in-out; }

/* ❌ NEVER: animate layout properties (width, height, top, left, margin, padding) */
/* ❌ NEVER: animate box-shadow (use opacity instead) */
/* ❌ NEVER: animations > 500ms on interactive elements */
```

### Motion timing standards
```
Micro (hover, focus):  150ms ease
Standard (transitions): 300ms ease-in-out
Emphasis (celebrations): 500ms ease-out
Page transitions:       250ms ease-in-out
```

### Celebration animations
```
Chapter complete:   framer-motion confetti burst from center + scale pulse on ring
Streak milestone:   fire emoji (🔥) scale 1→1.5→1 + text appears
Daily goal done:    green checkmark draws (stroke animation)
First login:        welcome message slides up (translateY 20px → 0)
```

---

## 10. LOADING STATES

### Hierarchy (ALWAYS use in this order)
```
1. Skeleton screens (PREFERRED — best perceived performance)
2. Inline spinner (for smaller components like buttons)
3. Text indicator ("Loading chapters...") — last resort only

RULE: Every page that loads async data MUST show skeleton first.
RULE: Buttons that trigger async actions MUST show spinner and disable.
RULE: Never show empty UI without explanation.
```

### Skeleton examples
```tsx
// Chapter list skeleton
<div className="space-y-3">
  {Array.from({length: 5}).map((_, i) => (
    <div key={i} className="h-20 rounded-lg bg-neutral-200 dark:bg-neutral-700 animate-pulse" />
  ))}
</div>

// Progress ring skeleton
<div className="h-20 w-20 rounded-full bg-neutral-200 dark:bg-neutral-700 animate-pulse" />

// StatCard skeleton
<div className="h-24 rounded-lg bg-neutral-200 dark:bg-neutral-700 animate-pulse" />
```

---

## 11. EMPTY STATES

Every list/collection must have an empty state:
```tsx
// Pattern:
<EmptyState
  icon={<BookOpen className="h-12 w-12 text-neutral-400" />}
  title="No chapters started yet"
  description="Pick a subject below to begin your NEET preparation"
  action={<Button>Browse Syllabus</Button>}
/>

// Subject-specific empties:
// No notes for chapter → "Upload your notes to get AI analysis"
// No quiz taken → "Take your first quiz to discover weak areas"
// No chat history → "Ask anything about this chapter"
// Roadmap not generated → "Set your exam date to get a personalized plan"
```

---

## 12. ERROR STATES

```tsx
// Pattern for failed data loads:
<ErrorState
  title="Couldn't load chapters"
  description="Check your connection and try again"
  action={<Button onClick={retry} variant="outline">Try Again</Button>}
/>

// Specific error messages (NOT generic "Something went wrong"):
// Network offline:    "You're offline — showing saved data"
// API key invalid:    "Your API key isn't working — check it in Settings"
// Rate limited:       "Too many requests — wait 30 seconds"
// LLM timeout:        "AI is taking too long — try again or switch provider"
// File too large:     "File is over 10MB — try compressing it first"
// OCR failed:         "Couldn't read this image — try better lighting"
```

---

## 13. ACCESSIBILITY REQUIREMENTS

```
Minimum contrast ratios:
  Normal text: 4.5:1
  Large text (18px+): 3:1
  UI components (borders, focus rings): 3:1

Focus indicators:
  NEVER: remove outline without replacement
  DO: ring-2 ring-brand-500 ring-offset-2 on all interactive elements

Touch targets:
  MINIMUM: 44×44px for all interactive elements
  Checkboxes: wrap in 44px container even if visual is 18px

Screen reader support:
  All images: meaningful alt text (or alt="" for decorative)
  All icons: aria-label on icon buttons
  Checkboxes: aria-label="Mark [subtopic name] as complete"
  Progress rings: aria-valuenow, aria-valuemin, aria-valuemax, role="progressbar"
  Status updates: aria-live="polite" for completion notifications

Keyboard navigation:
  Tab order: logical, top-to-bottom, left-to-right
  Enter/Space: activate buttons and checkboxes
  Escape: close modals, drawers, bottom sheets
  Arrow keys: navigate within list components
```

---

## 14. RESPONSIVE DESIGN RULES

```
Mobile (default, 375px):
  - Single column layout
  - Bottom navigation
  - Cards full-width (no grid)
  - Text sizes: base for content, sm for metadata
  - Touch-optimized (44px targets, swipe gestures)

Tablet (sm: 640px):
  - 2-column card grid where appropriate
  - Wider padding (px-6 instead of px-4)
  - Still BottomNav

Tablet landscape (md: 768px):
  - Subject filter becomes horizontal tabs (not dropdown)
  - Chapter grid: 2 columns
  - SideNav starts to appear (can toggle)

Desktop (lg: 1024px):
  - SideNav fixed at 240px
  - No BottomNav
  - Chapter grid: 3 columns
  - Chat panel: side panel (not drawer)
  - Analytics: multi-column dashboard

Large (xl: 1280px):
  - Max content width: 1200px, centered
  - Analytics: 4-column stat grid
```

---

## 15. DO / DON'T SUMMARY

```
✅ DO:
  - Mobile-first CSS always
  - Skeleton screens before any async content
  - Dark: variants on every color class
  - Subject colors for Physics/Chemistry/Biology elements
  - 44px minimum tap targets
  - Explicit aria-labels on all interactive elements
  - Optimistic UI updates with rollback
  - Framer Motion for non-trivial animations
  - DOMPurify on all user-generated content before render

❌ DON'T:
  - Hardcode hex colors (use CSS tokens or Tailwind classes)
  - Desktop-first CSS
  - Spinners as primary loading state (use skeletons)
  - "Something went wrong" generic errors
  - Remove focus outlines
  - Use arbitrary Tailwind values [450px] — use design tokens
  - Animate layout properties (width, height, top, left)
  - Render markdown without react-markdown + rehype-sanitize
  - Use <div onClick> instead of <button> for interactive elements
  - Mix raw HTML inputs with shadcn components
```

---

*SKILL_DESIGN.md — StudyOS Enterprise Design System | May 2026*
*Read before: any UI component, page layout, styling, animation, dark mode, responsiveness*
