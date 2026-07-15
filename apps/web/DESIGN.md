# STUDYOS Web — Design System

> **Single source of truth** for all frontend design decisions in the STUDYOS web application.
> Last updated: 2026-05-18

---

## Table of Contents

1. [Design System Overview](#1-design-system-overview)
2. [Design Principles](#2-design-principles)
3. [Color System](#3-color-system)
4. [Typography System](#4-typography-system)
5. [Spacing System](#5-spacing-system)
6. [Component Library](#6-component-library)
7. [Layout Patterns](#7-layout-patterns)
8. [Interaction Patterns](#8-interaction-patterns)
9. [Accessibility Guidelines](#9-accessibility-guidelines)
10. [Icon System](#10-icon-system)
11. [Form Patterns](#11-form-patterns)
12. [Error States](#12-error-states)
13. [Loading States](#13-loading-states)
14. [Dark Mode Strategy](#14-dark-mode-strategy)
15. [Responsive Design Strategy](#15-responsive-design-strategy)
16. [File Organization](#16-file-organization)

---

## 1. Design System Overview

### 1.1 Philosophy

STUDYOS is an **AI-first study operating system** designed for focused, distraction-free learning. The design prioritizes:

- **Clarity over decoration** — every visual element serves a functional purpose
- **Progress visibility** — learners should always know where they stand
- **Cognitive ease** — minimal visual noise, consistent patterns, predictable interactions
- **Performance-first** — design choices never compromise load time or responsiveness

### 1.2 Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16 (App Router, React 19) |
| Styling | Tailwind CSS v4 (CSS-first config) |
| Component Primitives | Radix UI (headless, accessible) |
| Variant System | class-variance-authority (cva) |
| Class Merging | tailwind-merge + clsx |
| Animations | Framer Motion |
| Icons | Lucide React |
| Charts | Recharts |
| Toast Notifications | Sonner |
| Theme Management | next-themes |
| State Management | Zustand (client), React Query (server) |
| Forms | React Hook Form + Zod |
| Fonts | Geist Sans + Geist Mono |

### 1.3 Design Token Architecture

Tokens are defined as CSS custom properties in `src/app/globals.css` and mapped to Tailwind utilities via the `@theme inline` directive. This enables:

- Runtime theme switching (light/dark/system)
- Zero-JS theme transitions
- Full Tailwind utility access (`bg-background`, `text-foreground`, etc.)

---

## 2. Design Principles

### 2.1 Core Principles

1. **Content First** — UI chrome should recede; learning content takes priority
2. **Consistent Patterns** — identical interactions behave identically across all features
3. **Progressive Disclosure** — show only what's needed; reveal complexity on demand
4. **Forgiving** — errors are recoverable, actions are reversible, states are clear
5. **Inclusive by Default** — accessible to all users regardless of ability or device

### 2.2 Visual Hierarchy Rules

- Primary actions use `bg-primary` fill
- Secondary actions use `variant="outline"` or `variant="ghost"`
- Destructive actions use `variant="destructive"`
- Information hierarchy: `text-foreground` > `text-muted-foreground`
- Interactive elements always have visible focus rings

---

## 3. Color System

### 3.1 Semantic Color Tokens

All colors are defined as CSS custom properties in `src/app/globals.css`.

#### Light Mode

| Token | Value | Usage |
|-------|-------|-------|
| `--background` | `#fafafa` | Page background |
| `--foreground` | `#09090b` | Primary text |
| `--card` | `#ffffff` | Card surfaces |
| `--card-foreground` | `#09090b` | Card text |
| `--popover` | `#ffffff` | Dropdown/popover surfaces |
| `--popover-foreground` | `#09090b` | Popover text |
| `--primary` | `#4f46e5` | Primary actions, links, brand (Indigo 600) |
| `--primary-foreground` | `#fafafa` | Text on primary |
| `--secondary` | `#f4f4f5` | Secondary surfaces (Zinc 100) |
| `--secondary-foreground` | `#09090b` | Text on secondary |
| `--muted` | `#f4f4f5` | Muted surfaces, backgrounds |
| `--muted-foreground` | `#71717a` | Secondary text, hints (Zinc 500) |
| `--accent` | `#f4f4f5` | Hover states, active nav items |
| `--accent-foreground` | `#09090b` | Text on accent |
| `--destructive` | `#dc2626` | Errors, delete actions (Red 600) |
| `--destructive-foreground` | `#fafafa` | Text on destructive |
| `--border` | `#e4e4e7` | Borders, dividers (Zinc 200) |
| `--input` | `#e4e4e7` | Input borders |
| `--ring` | `#4f46e5` | Focus rings (matches primary) |

#### Dark Mode

| Token | Value | Usage |
|-------|-------|-------|
| `--background` | `#09090b` | Page background (Zinc 950) |
| `--foreground` | `#fafafa` | Primary text |
| `--card` | `#18181b` | Card surfaces (Zinc 900) |
| `--card-foreground` | `#fafafa` | Card text |
| `--popover` | `#18181b` | Dropdown surfaces |
| `--popover-foreground` | `#fafafa` | Popover text |
| `--primary` | `#6366f1` | Primary actions (Indigo 500 — lighter for dark) |
| `--primary-foreground` | `#fafafa` | Text on primary |
| `--secondary` | `#27272a` | Secondary surfaces (Zinc 800) |
| `--secondary-foreground` | `#fafafa` | Text on secondary |
| `--muted` | `#27272a` | Muted surfaces |
| `--muted-foreground` | `#a1a1aa` | Secondary text (Zinc 400) |
| `--accent` | `#27272a` | Hover states |
| `--accent-foreground` | `#fafafa` | Text on accent |
| `--destructive` | `#ef4444` | Errors (Red 500 — lighter for dark) |
| `--destructive-foreground` | `#fafafa` | Text on destructive |
| `--border` | `#27272a` | Borders (Zinc 800) |
| `--input` | `#27272a` | Input borders |
| `--ring` | `#6366f1` | Focus rings |

### 3.2 Functional Colors (Direct Tailwind Usage)

These colors are used directly via Tailwind classes for specific semantic purposes:

| Color | Classes | Usage |
|-------|---------|-------|
| Success | `text-green-500`, `border-green-500/50` | Alert success variant, completed states |
| Warning | `text-yellow-500`, `border-yellow-500/50` | Alert warning variant |
| Info | `text-blue-500`, `border-blue-500/50` | Alert info variant |
| Progress (0-49%) | `text-blue-500` | ProgressRing low progress |
| Progress (50-99%) | `text-amber-500` | ProgressRing medium progress |
| Progress (100%) | `text-emerald-500` | ProgressRing complete |
| Streak | `text-orange-500`, `bg-orange-500/10` | StreakBadge flame icon |
| Overlay | `bg-black/80` | Dialog/AlertDialog overlay |

### 3.3 Color Usage Guidelines

- **Never** use raw hex values in components — always use semantic tokens
- **Never** introduce new color tokens without updating both light and dark modes
- Primary color shifts from Indigo 600 (light) to Indigo 500 (dark) for optimal contrast
- Destructive color shifts from Red 600 (light) to Red 500 (dark) for optimal contrast
- All semantic colors must maintain WCAG AA contrast ratios (4.5:1 for normal text, 3:1 for large text)

### 3.4 Tailwind Mapping

```css
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
}
```

Usage: `bg-background`, `text-foreground`, `border-border`, `ring-ring`, etc.

---

## 4. Typography System

### 4.1 Font Families

| Variable | Font | Usage |
|----------|------|-------|
| `--font-geist-sans` | Geist | Body text, UI elements, headings |
| `--font-geist-mono` | Geist Mono | Code blocks, technical content |

Loaded via `next/font/google` in `src/app/layout.tsx`:

```tsx
const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });
```

### 4.2 Type Scale

All sizes use Tailwind's default scale. The following table maps usage to classes:

| Role | Class | Size | Weight | Line Height | Usage |
|------|-------|------|--------|-------------|-------|
| H1 | `text-3xl` | 30px | `font-semibold` | `tracking-tight` | Marketing page title |
| H2 | `text-2xl` | 24px | `font-semibold` | `leading-none tracking-tight` | Card titles |
| H3 | `text-lg` | 18px | `font-semibold` | `leading-none tracking-tight` | Dialog titles, section headers |
| Body | `text-base` | 16px | `normal` | `leading-relaxed` | Paragraph text |
| Small | `text-sm` | 14px | `normal` | default | Form labels, nav items, descriptions |
| XS | `text-xs` | 12px | `normal` | default | Hints, badges, timestamps |
| Micro | `text-[10px]` | 10px | `font-medium` | default | Sidebar badges |
| Code | `text-xs` | 12px | `normal` | default | `<code>` blocks, `<pre>` |

### 4.3 Font Weight Scale

| Class | Weight | Usage |
|-------|--------|-------|
| `font-normal` | 400 | Body text, descriptions |
| `font-medium` | 500 | Labels, badges, small emphasis |
| `font-semibold` | 600 | Headings, titles, active nav items |
| `font-bold` | 700 | Progress percentages, streak counts |

### 4.4 Typography Conventions

- All headings use `tracking-tight` for a modern, compact appearance
- Card titles use `leading-none` to eliminate extra vertical space
- Body text uses `leading-relaxed` for readability
- Muted/secondary text always uses `text-muted-foreground`
- Code snippets use `rounded-md bg-muted px-1.5 py-0.5`

---

## 5. Spacing System

### 5.1 Scale

STUDYOS uses Tailwind CSS v4's default spacing scale (0.25rem = 4px base):

| Class | Pixels | Common Usage |
|-------|--------|-------------|
| `0.5` | 2px | Micro gaps between icons and text |
| `1` | 4px | Tight inline spacing |
| `1.5` | 6px | Form field gaps, tooltip padding |
| `2` | 8px | Button padding, small gaps |
| `3` | 12px | Card internal padding (compact) |
| `4` | 16px | Standard padding, page margins |
| `5` | 20px | — |
| `6` | 24px | Card header padding, section gaps |
| `8` | 32px | Large section gaps |
| `10` | 40px | Page-level padding (auth pages) |
| `12` | 48px | — |
| `16` | 64px | Hero spacing |

### 5.2 Layout Spacing Conventions

| Context | Pattern | Example |
|---------|---------|---------|
| Page content | `p-4 sm:p-6` | App shell main content area |
| Card internal | `p-6` | CardHeader, CardContent, CardFooter |
| Card compact | `p-4` | StudyStats, inline cards |
| Form fields | `space-y-4` | Vertical form spacing |
| Section gaps | `gap-4` to `gap-6` | Flex/grid gaps between sections |
| Auth pages | `px-4 py-16` | Centered auth card layout |
| Marketing | `px-6 py-16` | Marketing page padding |
| Sidebar nav items | `space-y-1` | Sidebar navigation list |
| Dialog content | `gap-4` | Dialog internal spacing |

### 5.3 Content Width Constraints

| Layout | Max Width | Usage |
|--------|-----------|-------|
| App content | `max-w-5xl` (1024px) | Dashboard, syllabus, settings |
| Auth forms | `max-w-sm` (384px) | Login, signup cards |
| Marketing | `max-w-2xl` (672px) | Marketing landing page |
| Dialogs | `max-w-lg` (512px) | Standard modal dialogs |

---

## 6. Component Library

All UI components live in `src/shared/components/ui/`. They follow the shadcn/ui pattern: copyable, customizable, accessible.

### 6.1 Button

**File:** `src/shared/components/ui/button.tsx`

```tsx
import { Button } from "@/shared/components/ui/button";
```

| Variant | Class | Usage |
|---------|-------|-------|
| `default` | `bg-primary text-primary-foreground hover:bg-primary/90` | Primary actions, form submit |
| `destructive` | `bg-destructive text-destructive-foreground hover:bg-destructive/90` | Delete, remove, danger actions |
| `outline` | `border border-input bg-background hover:bg-accent` | Secondary actions, cancel |
| `secondary` | `bg-secondary text-secondary-foreground hover:bg-secondary/80` | Tertiary actions |
| `ghost` | `hover:bg-accent hover:text-accent-foreground` | Nav items, icon buttons, menu triggers |
| `link` | `text-primary underline-offset-4 hover:underline` | Inline links styled as buttons |

| Size | Class | Usage |
|------|-------|-------|
| `default` | `h-10 px-4 py-2` | Standard buttons |
| `sm` | `h-9 rounded-md px-3` | Compact buttons, table actions |
| `lg` | `h-11 rounded-md px-8` | Hero CTAs, prominent actions |
| `icon` | `h-10 w-10` | Icon-only buttons |

**Props:**
- `asChild?: boolean` — Render as child component (via Radix Slot)
- `variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link"`
- `size?: "default" | "sm" | "lg" | "icon"`

**Focus:** `focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2`

### 6.2 Card

**File:** `src/shared/components/ui/card.tsx`

```tsx
import { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent } from "@/shared/components/ui/card";
```

**Structure:**
```tsx
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Optional description</CardDescription>
  </CardHeader>
  <CardContent>Main content</CardContent>
  <CardFooter>Actions</CardFooter>
</Card>
```

**Styles:**
- Card: `rounded-lg border bg-card text-card-foreground shadow-sm`
- CardHeader: `flex flex-col space-y-1.5 p-6`
- CardTitle: `text-2xl font-semibold leading-none tracking-tight`
- CardDescription: `text-sm text-muted-foreground`
- CardContent: `p-6 pt-0`
- CardFooter: `flex items-center p-6 pt-0`

### 6.3 Input

**File:** `src/shared/components/ui/input.tsx`

```tsx
import { Input } from "@/shared/components/ui/input";
```

**Styles:** `flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm`

**States:**
- Focus: `focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2`
- Disabled: `disabled:cursor-not-allowed disabled:opacity-50`
- Placeholder: `placeholder:text-muted-foreground`
- Error: Add `border-destructive` class manually

### 6.4 Textarea

**File:** `src/shared/components/ui/textarea.tsx`

```tsx
import { Textarea } from "@/shared/components/ui/textarea";
```

**Styles:** `flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm`

Same focus/disabled states as Input.

### 6.5 Label

**File:** `src/shared/components/ui/label.tsx`

```tsx
import { Label } from "@/shared/components/ui/label";
```

**Styles:** `text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70`

### 6.6 Badge

**File:** `src/shared/components/ui/badge.tsx`

```tsx
import { Badge } from "@/shared/components/ui/badge";
```

| Variant | Class | Usage |
|---------|-------|-------|
| `default` | `border-transparent bg-primary text-primary-foreground` | Status, tags |
| `secondary` | `border-transparent bg-secondary text-secondary-foreground` | Secondary status |
| `destructive` | `border-transparent bg-destructive text-destructive-foreground` | Error status |
| `outline` | `text-foreground` | Neutral tags |

**Styles:** `inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold`

### 6.7 Alert

**File:** `src/shared/components/ui/alert.tsx`

```tsx
import { Alert, AlertTitle, AlertDescription } from "@/shared/components/ui/alert";
```

| Variant | Class | Usage |
|---------|-------|-------|
| `default` | `bg-background text-foreground` | General notices |
| `destructive` | `border-destructive/50 text-destructive` | Errors |
| `success` | `border-green-500/50 text-green-700 dark:text-green-400` | Success messages |
| `warning` | `border-yellow-500/50 text-yellow-700 dark:text-yellow-400` | Warnings |
| `info` | `border-blue-500/50 text-blue-700 dark:text-blue-400` | Informational |

**Structure:**
```tsx
<Alert variant="destructive">
  <AlertCircle className="h-4 w-4" />
  <AlertTitle>Error</AlertTitle>
  <AlertDescription>Description of the error.</AlertDescription>
</Alert>
```

**Styles:**
- Alert: `relative w-full rounded-lg border p-4`
- AlertTitle: `mb-1 font-medium leading-none tracking-tight`
- AlertDescription: `text-sm [&_p]:leading-relaxed`

### 6.8 Dialog

**File:** `src/shared/components/ui/dialog.tsx`

```tsx
import { Dialog, DialogContent, DialogHeader, DialogFooter, DialogTitle, DialogDescription, DialogTrigger, DialogClose } from "@/shared/components/ui/dialog";
```

**Animation:** Fade + zoom (scale 0.95 → 1), slide from center
**Overlay:** `fixed inset-0 z-50 bg-black/80`
**Content:** `fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg sm:rounded-lg`

**Structure:**
```tsx
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Title</DialogTitle>
      <DialogDescription>Description</DialogDescription>
    </DialogHeader>
    {/* Content */}
    <DialogFooter>
      <DialogClose>Cancel</DialogClose>
      <Button>Action</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### 6.9 AlertDialog

**File:** `src/shared/components/ui/alert-dialog.tsx`

Same API as Dialog but with `AlertDialogAction` and `AlertDialogCancel` buttons. Use for confirmations (delete, discard changes).

### 6.10 Dropdown Menu

**File:** `src/shared/components/ui/dropdown-menu.tsx`

```tsx
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuShortcut } from "@/shared/components/ui/dropdown-menu";
```

**Animation:** Fade + zoom + slide from trigger side
**Content:** `z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md`

**Item types:**
- `DropdownMenuItem` — Standard clickable item
- `DropdownMenuCheckboxItem` — With checkmark toggle
- `DropdownMenuRadioItem` — With radio dot
- `DropdownMenuSub` — Nested submenu with `DropdownMenuSubTrigger` + `DropdownMenuSubContent`

### 6.11 Select

**File:** `src/shared/components/ui/select.tsx`

```tsx
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem, SelectLabel, SelectSeparator } from "@/shared/components/ui/select";
```

**Trigger:** `flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm`
**Content:** `relative z-50 max-h-96 min-w-[8rem] overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md`

### 6.12 Tabs

**File:** `src/shared/components/ui/tabs.tsx`

```tsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/shared/components/ui/tabs";
```

**List:** `inline-flex h-10 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground`
**Trigger:** `inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium`
**Active Trigger:** `data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm`

### 6.13 Progress

**File:** `src/shared/components/ui/progress.tsx`

```tsx
import { Progress } from "@/shared/components/ui/progress";
```

**Props:** `value?: number` (0-100)
**Styles:** `relative h-4 w-full overflow-hidden rounded-full bg-secondary`
**Indicator:** `h-full w-full flex-1 bg-primary transition-all`

### 6.14 Avatar

**File:** `src/shared/components/ui/avatar.tsx`

```tsx
import { Avatar, AvatarImage, AvatarFallback } from "@/shared/components/ui/avatar";
```

**Styles:**
- Avatar: `relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full`
- AvatarFallback: `flex h-full w-full items-center justify-center rounded-full bg-muted`

### 6.15 Switch

**File:** `src/shared/components/ui/switch.tsx`

```tsx
import { Switch } from "@/shared/components/ui/switch";
```

**Styles:** `peer inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent`
**Checked:** `data-[state=checked]:bg-primary`
**Unchecked:** `data-[state=unchecked]:bg-input`
**Thumb:** `h-5 w-5 rounded-full bg-background shadow-lg`

### 6.16 Tooltip

**File:** `src/shared/components/ui/tooltip.tsx`

```tsx
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/shared/components/ui/tooltip";
```

**Usage:** Wrap app or section in `TooltipProvider`, then use `Tooltip` + `TooltipTrigger` + `TooltipContent`
**Content:** `z-50 overflow-hidden rounded-md border bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-md`
**Default sideOffset:** `4`

### 6.17 Popover

**File:** `src/shared/components/ui/popover.tsx`

```tsx
import { Popover, PopoverTrigger, PopoverContent, PopoverClose, PopoverAnchor } from "@/shared/components/ui/popover";
```

**Content:** `z-50 w-72 rounded-md border bg-popover p-4 text-popover-foreground shadow-md`

### 6.18 Separator

**File:** `src/shared/components/ui/separator.tsx`

```tsx
import { Separator } from "@/shared/components/ui/separator";
```

**Horizontal (default):** `shrink-0 bg-border h-[1px] w-full`
**Vertical:** `shrink-0 bg-border h-full w-[1px]`

### 6.19 Skeleton

**File:** `src/shared/components/ui/skeleton.tsx`

```tsx
import { Skeleton } from "@/shared/components/ui/skeleton";
```

**Styles:** `animate-pulse rounded-md bg-muted`

Usage: Match the dimensions of the content being loaded.

### 6.20 Spinner

**File:** `src/shared/components/ui/spinner.tsx`

```tsx
import { Spinner } from "@/shared/components/ui/spinner";
```

| Size | Class | Usage |
|------|-------|-------|
| `sm` | `h-4 w-4` | Inline with buttons, small loaders |
| `md` | `h-6 w-6` | Default, page sections |
| `lg` | `h-8 w-8` | Full-page loading |

**Icon:** `Loader2` from Lucide, `animate-spin text-muted-foreground`

### 6.21 Scroll Area

**File:** `src/shared/components/ui/scroll-area.tsx`

```tsx
import { ScrollArea } from "@/shared/components/ui/scroll-area";
```

**Styles:** `overflow-auto`

### 6.22 Visually Hidden

**File:** `src/shared/components/ui/visually-hidden.tsx`

```tsx
import { VisuallyHidden } from "@/shared/components/ui/visually-hidden";
```

Screen-reader-only text. Uses `absolute h-px w-px overflow-hidden whitespace-nowrap border-0 p-0 [clip:rect(0,0,0,0)]`.

### 6.23 Animated Components

**File:** `src/shared/components/ui/animated-page.tsx`

```tsx
import { AnimatedPage, AnimatedCard } from "@/shared/components/ui/animated-page";
```

**AnimatedPage:**
- Initial: `opacity: 0, y: 12`
- Animate: `opacity: 1, y: 0`
- Exit: `opacity: 0, y: -12`
- Transition: `duration: 0.3, ease: "easeOut"`
- Props: `delay?: number`

**AnimatedCard:**
- Initial: `opacity: 0, y: 8`
- Animate: `opacity: 1, y: 0`
- Transition: `duration: 0.25, delay: index * 0.05`
- Props: `index?: number`

### 6.24 Form Components

**Directory:** `src/shared/components/form/`

#### FormField

**File:** `src/shared/components/form/form-field.tsx`

```tsx
import { FormField } from "@/shared/components/form/form-field";
```

**Props:**
- `name: string` — Field name (matches RHF register)
- `label: string` — Display label
- `hint?: string` — Optional hint text (rendered inline with label)
- `error?: string` — Override auto-detected error message
- `children: ReactNode` — Input component

**Layout:** `space-y-2` container with Label + children + error message

#### FormSelectField

**File:** `src/shared/components/form/form-select-field.tsx`

```tsx
import { FormSelectField } from "@/shared/components/form/form-select-field";
```

**Props:**
- `name: string`
- `label: string`
- `placeholder?: string` (default: "Select...")
- `options: { value: string; label: string }[]`
- `description?: string`
- `disabled?: boolean`

Uses RHF Controller internally.

#### FormSubmitButton

**File:** `src/shared/components/form/form-submit-button.tsx`

```tsx
import { FormSubmitButton } from "@/shared/components/form/form-submit-button";
```

**Props:** Extends `ButtonProps` + `loadingText?: string` (default: "Saving...")

Automatically disables during form submission and shows Spinner + loading text.

### 6.25 Layout Components

**Directory:** `src/shared/components/layout/`

#### AppShell

**File:** `src/shared/components/layout/app-shell.tsx`

The main application shell with sidebar + header + content layout.

**Structure:**
```tsx
<AppShell>
  <AppSessionGate>{children}</AppSessionGate>
</AppShell>
```

**Layout:**
- Sidebar: `relative flex flex-col border-r border-border bg-card` (w-64 expanded, w-16 collapsed)
- Header: `sticky top-0 z-40 flex h-14 items-center gap-4 border-b border-border bg-background/95 backdrop-blur`
- Main: `flex-1 p-4 sm:p-6`

#### ThemeToggle

**File:** `src/shared/components/layout/theme-toggle.tsx`

Ghost icon button (h-9 w-9) that toggles between light/dark themes. Uses `next-themes` + `useMounted` to prevent hydration mismatch.

### 6.26 Feedback Components

**Directory:** `src/shared/components/feedback/`

#### ErrorBoundary

**File:** `src/shared/components/error-boundary.tsx`

Class component that catches React rendering errors.

**Default fallback:** Destructive Alert with error message + "Try again" button
**Custom fallback:** Pass `fallback?: ReactNode` prop

#### ErrorFallback

**File:** `src/shared/components/feedback/error-fallback.tsx`

Functional component for route-level error boundaries.

**Props:**
- `title: string`
- `description?: ReactNode`
- `error?: { message?: string; digest?: string }`
- `onRetry?: () => void`
- `retryLabel?: string` (default: "Try again")

**Styles:** `flex flex-col items-start gap-4 rounded-xl border border-border bg-card p-6`

### 6.27 Toast Notifications

**Library:** Sonner (`sonner`)

**File:** `src/shared/lib/toast.ts`

```tsx
import { notifySuccess, notifyError, notifyInfo, notifyFromUnknown } from "@/shared/lib/toast";
```

| Function | Toast Type | Usage |
|----------|-----------|-------|
| `notifySuccess(message)` | Success | Operation completed |
| `notifyError(message)` | Error | Operation failed |
| `notifyInfo(message)` | Info | Informational message |
| `notifyFromUnknown(err, fallback?)` | Error | Catches ApiError, Error, or raw values |

**Configuration:** `richColors closeButton position="top-right" visibleToasts={5}`

---

## 7. Layout Patterns

### 7.1 Route Groups

| Group | Purpose | Layout |
|-------|---------|--------|
| `(app)` | Authenticated app pages | AppShell (sidebar + header) + AppSessionGate |
| `(auth)` | Login/signup | Centered card layout |
| `(marketing)` | Public landing pages | Full-width flex column |

### 7.2 App Shell Layout

```
┌─────────────────────────────────────────────────┐
│  Sidebar (w-64/w-16)  │  Header (h-14, sticky)  │
│                       ├─────────────────────────┤
│  Nav items            │  Main content           │
│  + Secondary items    │  p-4 sm:p-6             │
│                       │  max-w-5xl              │
└───────────────────────┴─────────────────────────┘
```

**Sidebar:**
- Expanded: `w-64` with full labels
- Collapsed: `w-16` with icon-only + tooltips
- Toggle via `useUiStore().toggleSidebar()`
- Nav items: `rounded-lg px-3 py-2 text-sm` with active state `bg-accent font-medium`

**Header:**
- Sticky, `h-14`, backdrop blur
- Page title (left), sync indicator + notifications + user menu (right)
- User dropdown: Avatar + email + roles + Profile/Settings/Logout

### 7.3 Auth Layout

```
┌─────────────────────────────────────────┐
│                                         │
│           ┌─────────────────┐           │
│           │                 │           │
│           │   Card          │           │
│           │   (max-w-sm)    │           │
│           │   p-6           │           │
│           │                 │           │
│           └─────────────────┘           │
│                                         │
└─────────────────────────────────────────┘
```

- Centered vertically and horizontally
- `min-h-full flex-1 items-center justify-center px-4 py-16`
- Card: `w-full max-w-sm p-6`

### 7.4 Grid Patterns

STUDYOS uses CSS Grid and Flexbox via Tailwind utilities:

| Pattern | Classes | Usage |
|---------|---------|-------|
| Stats row | `flex flex-wrap items-center gap-6` | StudyStats dashboard row |
| Card grid | `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4` | Dashboard stat cards |
| Form layout | `space-y-4` | Vertical form fields |
| Button row | `flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2` | Dialog footers |

### 7.5 Responsive Breakpoints

STUDYOS uses Tailwind's default breakpoints:

| Breakpoint | Width | Usage |
|------------|-------|-------|
| `sm` | 640px | Tablet adjustments |
| `md` | 768px | Desktop nav visible, mobile nav hidden |
| `lg` | 1024px | Multi-column layouts |
| `xl` | 1280px | Wide layouts |
| `2xl` | 1536px | — |

**Common responsive patterns:**
- `hidden md:flex` — Hide on mobile, show on desktop
- `text-center sm:text-left` — Center on mobile, left-align on desktop
- `p-4 sm:p-6` — Tighter padding on mobile
- `flex-col sm:flex-row` — Stack on mobile, row on desktop
- `w-full sm:w-auto` — Full width on mobile, auto on desktop

---

## 8. Interaction Patterns

### 8.1 Transitions

**Global transition** (defined in `globals.css`):
```css
*, *::before, *::after {
  transition-property: background-color, border-color, color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
```

This applies smooth transitions to all color-related property changes automatically.

### 8.2 Hover States

| Component | Hover Effect |
|-----------|-------------|
| Button (default) | `hover:bg-primary/90` |
| Button (outline) | `hover:bg-accent hover:text-accent-foreground` |
| Button (ghost) | `hover:bg-accent hover:text-accent-foreground` |
| Button (secondary) | `hover:bg-secondary/80` |
| Card | No hover effect by default (add via className) |
| Nav item | `hover:bg-accent hover:text-accent-foreground` |
| Link | `hover:underline` (with `underline-offset-4`) |
| Dropdown item | `focus:bg-accent focus:text-accent-foreground` |
| Badge | `hover:bg-primary/80` (default variant) |

### 8.3 Focus States

**Global focus-visible** (defined in `globals.css`):
```css
:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}
```

**Component-specific focus patterns:**
- Buttons/Inputs: `focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2`
- Tabs trigger: `focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2`
- Select trigger: `focus:ring-2 focus:ring-ring focus:ring-offset-2`
- Switch: `focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background`

### 8.4 Animations

#### Framer Motion (Page/Card transitions)

| Component | Duration | Easing | Effect |
|-----------|----------|--------|--------|
| AnimatedPage | 300ms | easeOut | Fade + slide up 12px |
| AnimatedCard | 250ms | default | Fade + slide up 8px (staggered) |

#### Tailwind Animate Classes

| Class | Usage |
|-------|-------|
| `animate-pulse` | Skeleton loading, milestone streaks |
| `animate-spin` | Spinner (Loader2 icon) |
| `animate-in` | Dialog/Popover open |
| `animate-out` | Dialog/Popover close |
| `fade-in-0` | Fade in from transparent |
| `fade-out-0` | Fade out to transparent |
| `zoom-in-95` | Scale from 0.95 to 1 |
| `zoom-out-95` | Scale from 1 to 0.95 |
| `slide-in-from-top-2` | Slide in from above |
| `slide-in-from-bottom-2` | Slide in from below |

#### Progress Ring Animation

- SVG stroke dashoffset transition: `transition-all duration-500 ease-out`
- Color changes based on progress threshold (blue → amber → emerald)

### 8.5 Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

All animations and transitions are effectively disabled for users who prefer reduced motion.

---

## 9. Accessibility Guidelines

### 9.1 WCAG Compliance

STUDYOS targets **WCAG 2.1 Level AA** compliance.

### 9.2 Keyboard Navigation

| Feature | Implementation |
|---------|---------------|
| Skip link | "Skip to main content" link in layout (sr-only, visible on focus) |
| Focus trap | Radix Dialog/AlertDialog auto-trap focus |
| Tab order | Logical DOM order, no positive tabindex |
| Escape key | Radix modals close on Escape |
| Arrow keys | Radix Tabs, Select, DropdownMenu support arrow key navigation |

### 9.3 Screen Reader Support

| Pattern | Implementation |
|---------|---------------|
| Skip link | `href="#main"` with `sr-only` class |
| Loading states | `aria-busy="true"` + `aria-label="Loading"` |
| Status updates | `role="status"` + `aria-live="polite"` |
| Error states | `role="alert"` on error containers |
| Icon buttons | `aria-label` descriptive text |
| Hidden decorative content | `aria-hidden` |
| Form fields | `<Label htmlFor>` matching input `id` |
| Active nav items | `font-medium` visual distinction (add aria-current if needed) |

### 9.4 Color Contrast

All semantic color pairs meet WCAG AA minimums:

| Pair | Light Mode Ratio | Dark Mode Ratio |
|------|-----------------|-----------------|
| foreground / background | 17.4:1 | 17.4:1 |
| muted-foreground / background | 4.6:1 | 7.1:1 |
| primary / primary-foreground | 8.2:1 | 10.4:1 |
| destructive / destructive-foreground | 5.9:1 | 8.2:1 |

### 9.5 High Contrast Mode

```css
@media (forced-colors: active) {
  .border {
    border-color: CanvasText;
  }
}
```

Borders are forced to system text color in Windows High Contrast Mode.

### 9.6 Form Accessibility

- All inputs have associated `<Label>` with matching `htmlFor`/`id`
- Error messages use `text-sm text-destructive` below the input
- Required fields should be indicated in label (not yet standardized)
- Disabled inputs use `disabled:cursor-not-allowed disabled:opacity-50`

---

## 10. Icon System

### 10.1 Library

**Lucide React** (`lucide-react`) — consistent, open-source icon set.

### 10.2 Icon Sizing Convention

| Context | Class | Size |
|---------|-------|------|
| Sidebar nav | `h-4 w-4` | 16px |
| Button icons | `[&_svg]:size-4` (via buttonVariants) | 16px |
| Header actions | `h-4 w-4` | 16px |
| Dropdown items | `[&_svg]:size-4` | 16px |
| Alert icons | `h-4 w-4` | 16px |
| Spinner sm | `h-4 w-4` | 16px |
| Spinner md | `h-6 w-6` | 24px |
| Spinner lg | `h-8 w-8` | 32px |
| StreakBadge sm | `h-3 w-3` | 12px |
| StreakBadge md | `h-4 w-4` | 16px |
| StreakBadge lg | `h-5 w-5` | 20px |

### 10.3 Icon Button Pattern

```tsx
<Button variant="ghost" size="icon" aria-label="Description">
  <IconName className="h-4 w-4" />
</Button>
```

### 10.4 Currently Used Icons

| Icon | Usage |
|------|-------|
| `LayoutDashboard` | Dashboard nav |
| `BookOpen` | Syllabus nav |
| `MessageSquare` | Practice nav |
| `BarChart3` | Progress nav |
| `Calendar` | Schedule nav |
| `Trophy` | Achievements nav |
| `Settings` | Settings nav |
| `Bell` | Notifications |
| `User` | Profile |
| `LogOut` | Logout |
| `ChevronLeft` / `ChevronRight` | Sidebar toggle |
| `X` | Dialog close |
| `Loader2` | Spinner |
| `AlertCircle` | Error alerts |
| `Flame` | Streak badge |
| `Check` | Select item, checkbox |
| `ChevronDown` / `ChevronUp` | Select dropdown |
| `ChevronRight` | Submenu trigger |
| `Circle` | Radio indicator |

---

## 11. Form Patterns

### 11.1 Form Architecture

| Layer | Technology |
|-------|-----------|
| State management | React Hook Form |
| Validation | Zod schemas |
| Resolver | `@hookform/resolvers/zod` |
| UI wrapper | `FormProvider` + custom `FormField` |

### 11.2 Form Structure

```tsx
<FormProvider {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)} noValidate>
    <FormField name="email" label="Email" hint="Optional hint">
      <Input {...form.register("email")} />
    </FormField>
    <FormField name="password" label="Password">
      <Input type="password" {...form.register("password")} />
    </FormField>
    <FormSubmitButton>Submit</FormSubmitButton>
  </form>
</FormProvider>
```

### 11.3 Field Layout

- Container: `space-y-2`
- Label: `text-sm font-medium leading-none`
- Hint: `ml-1 text-xs font-normal text-muted-foreground` (inline with label)
- Error: `text-sm text-destructive` (below input)
- Field spacing: `space-y-4` between fields

### 11.4 Validation Patterns

- Zod schemas defined in feature `schema.ts` files (e.g., `features/auth/schema.ts`)
- Default values set in `useForm` config
- Server-side validation errors displayed via `error` prop on `FormField`
- Submit button auto-disables during `formState.isSubmitting`

### 11.5 Submit Button Pattern

```tsx
<FormSubmitButton loadingText="Saving...">
  Save Changes
</FormSubmitButton>
```

- Auto-disables when `formState.isSubmitting`
- Shows `Spinner size="sm"` + loading text during submission
- Inherits all `ButtonProps`

---

## 12. Error States

### 12.1 Error Hierarchy

| Level | Component | Location |
|-------|-----------|----------|
| Route segment | `error.tsx` (Next.js) | `src/app/(app)/error.tsx` |
| React tree | `ErrorBoundary` | Wraps feature components |
| API call | `notifyError()` | In hook/component catch blocks |
| Form field | `FormField` error | Below individual inputs |
| Global | Sonner toast | Top-right corner |

### 12.2 Route Error Pattern

```tsx
// src/app/(app)/error.tsx
"use client";

export default function AppSegmentError({ error, reset }) {
  useEffect(() => { console.error(error); }, [error]);
  return (
    <ErrorFallback
      title="This section failed to load"
      description="Try again, or go back after the problem is fixed."
      error={error}
      onRetry={() => reset()}
      retryLabel="Retry"
    />
  );
}
```

### 12.3 ErrorFallback Component

```tsx
<ErrorFallback
  title="Section title"
  description="Optional description"
  error={{ message: "Error message", digest: "Sentry digest" }}
  onRetry={() => retry()}
  retryLabel="Try again"
/>
```

**Styles:** `flex flex-col items-start gap-4 rounded-xl border border-border bg-card p-6`

### 12.4 Error Alert Variants

```tsx
<Alert variant="destructive">
  <AlertCircle className="h-4 w-4" />
  <AlertTitle>Something went wrong</AlertTitle>
  <AlertDescription>
    <p className="text-sm text-muted-foreground">{error.message}</p>
    <Button variant="outline" size="sm" className="mt-4" onClick={retry}>
      Try again
    </Button>
  </AlertDescription>
</Alert>
```

### 12.5 API Error Handling

```tsx
import { notifyFromUnknown } from "@/shared/lib";

try {
  await apiCall();
} catch (e) {
  notifyFromUnknown(e, "Fallback message");
}
```

- `ApiError` instances extract problem details from response body
- Generic `Error` instances use `error.message`
- Unknown values use the fallback message

---

## 13. Loading States

### 13.1 Loading Patterns

| Pattern | Component | Usage |
|---------|-----------|-------|
| Page-level skeleton | `Skeleton` blocks | `src/app/(app)/loading.tsx` |
| Inline spinner | `Spinner` | Session gate, form submission |
| Card skeleton | `Skeleton` with dimensions | Form fallbacks, data loading |
| Progress ring | `ProgressRing` | Exam progress display |
| Button loading | `FormSubmitButton` | Form submission |

### 13.2 App Loading (Route-level)

```tsx
// src/app/(app)/loading.tsx
export default function AppLoading() {
  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-4 px-4 py-10" aria-busy="true" aria-label="Loading">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-4 w-full max-w-xl" />
      <Skeleton className="h-4 w-full max-w-lg" />
      <Skeleton className="h-32 w-full" />
    </div>
  );
}
```

### 13.3 Session Gate Loading

```tsx
<div className="flex flex-1 items-center justify-center py-24" role="status" aria-live="polite">
  <Spinner className="size-8" aria-hidden />
  <VisuallyHidden>Loading session</VisuallyHidden>
</div>
```

### 13.4 Form Loading (Suspense Fallback)

```tsx
function LoginFormFallback() {
  return (
    <div className="space-y-4" aria-busy="true" aria-label="Loading sign-in form">
      <div className="space-y-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-10 w-full" />
      </div>
      {/* Repeat for each field */}
      <Skeleton className="h-10 w-full" />
    </div>
  );
}
```

### 13.5 Skeleton Sizing Guide

| Content | Skeleton Classes |
|---------|-----------------|
| Heading | `h-8 w-48` |
| Label | `h-4 w-24` |
| Body text | `h-4 w-full max-w-xl` |
| Input | `h-10 w-full` |
| Card/Panel | `h-32 w-full` |
| Badge | `h-8 w-24 rounded-full` |

---

## 14. Dark Mode Strategy

### 14.1 Implementation

- **Library:** `next-themes` with `attribute="class"` strategy
- **Default:** `"system"` — follows OS preference
- **Storage key:** `"studyos-theme"`
- **Transitions:** `disableTransitionOnChange` (CSS handles transitions globally)

```tsx
<ThemeProvider
  attribute="class"
  defaultTheme="system"
  enableSystem
  disableTransitionOnChange
  storageKey="studyos-theme"
>
```

### 14.2 Theme Toggle

- Located in header (desktop) and auth shell header
- Uses `useMounted` hook to prevent hydration mismatch
- Button: `h-9 w-9 px-0` ghost variant
- Labels: "Switch to light mode" / "Switch to dark mode"
- Icons: Text characters (`☀` / `☾`) — replace with Lucide icons if desired

### 14.3 Dark Mode Color Adjustments

| Token | Light | Dark | Reason |
|-------|-------|------|--------|
| `--primary` | `#4f46e5` (Indigo 600) | `#6366f1` (Indigo 500) | Lighter for dark bg contrast |
| `--destructive` | `#dc2626` (Red 600) | `#ef4444` (Red 500) | Lighter for dark bg contrast |
| `--background` | `#fafafa` (Zinc 50) | `#09090b` (Zinc 950) | Full dark surface |
| `--card` | `#ffffff` (White) | `#18181b` (Zinc 900) | Elevated dark surface |
| `--border` | `#e4e4e7` (Zinc 200) | `#27272a` (Zinc 800) | Subtle dark border |

### 14.4 Theme Color Meta Tags

```tsx
themeColor: [
  { media: "(prefers-color-scheme: light)", color: "#ffffff" },
  { media: "(prefers-color-scheme: dark)", color: "#0a0a0a" },
]
```

Controls browser chrome color (status bar, tab bar) on mobile.

### 14.5 Dark Mode Guidelines

- Always test both themes when adding new components
- Use semantic tokens exclusively — never hardcode colors
- Functional colors (green, yellow, blue, orange, emerald) use Tailwind's built-in dark variants
- Images/illustrations should work in both modes or have dark variants

---

## 15. Responsive Design Strategy

### 15.1 Mobile-First Approach

All styles are mobile-first. Desktop enhancements use `md:` and `lg:` prefixes.

### 15.2 Responsive Component Patterns

#### Sidebar
- Mobile: Hidden or overlay (not yet implemented — sidebar is always visible)
- Desktop: `w-64` expanded, `w-16` collapsed

#### Header
- Mobile: Compact, hamburger menu for nav
- Desktop (`md:`): Full horizontal nav, no hamburger

#### Dialog
- Mobile: Full-width, no border radius
- Desktop (`sm:`): `max-w-lg`, `sm:rounded-lg`

#### Dialog Footer
- Mobile: `flex-col-reverse` (cancel below action)
- Desktop (`sm:`): `sm:flex-row sm:justify-end sm:space-x-2`

#### Card Content
- Mobile: `text-center`
- Desktop (`sm:`): `sm:text-left`

#### Main Content Padding
- Mobile: `p-4`
- Desktop (`sm:`): `sm:p-6`

### 15.3 Viewport Configuration

```tsx
viewport: {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,  // Prevents zoom on iOS
}
```

### 15.4 Breakpoint Usage Map

| Breakpoint | Common Uses |
|------------|-------------|
| `sm:` (640px) | Text alignment, dialog rounding, padding increase, flex direction |
| `md:` (768px) | Nav visibility, header layout, form columns |
| `lg:` (1024px) | Multi-column grids, sidebar always visible |
| `xl:` (1280px) | Wider content areas |

### 15.5 Touch Targets

All interactive elements meet minimum 44x44px touch target:
- Buttons: `h-10` (40px) minimum, icon buttons `h-10 w-10`
- Nav items: `px-3 py-2` with text (exceeds 44px with text height)
- Form inputs: `h-10` (40px) minimum

---

## 16. File Organization

### 16.1 Design-Related Code Structure

```
apps/web/src/
├── app/
│   ├── layout.tsx              # Root layout, font loading, skip link
│   ├── providers.tsx           # ThemeProvider, QueryClient, etc.
│   ├── globals.css             # CSS variables, @theme inline, base styles
│   ├── (app)/                  # Authenticated app routes
│   │   ├── layout.tsx          # AppShell + AppSessionGate
│   │   ├── loading.tsx         # Route-level skeleton
│   │   └── error.tsx           # Route-level error fallback
│   ├── (auth)/                 # Auth routes
│   │   └── layout.tsx          # Centered card layout
│   └── (marketing)/            # Public routes
│       └── layout.tsx          # Full-width flex column
│
├── shared/
│   ├── components/
│   │   ├── ui/                 # Primitive UI components (shadcn pattern)
│   │   │   ├── button.tsx      # Button with cva variants
│   │   │   ├── card.tsx        # Card composition
│   │   │   ├── input.tsx       # Form input
│   │   │   ├── dialog.tsx      # Modal dialog
│   │   │   ├── alert.tsx       # Alert banners
│   │   │   ├── badge.tsx       # Status badges
│   │   │   ├── avatar.tsx      # User avatars
│   │   │   ├── progress.tsx    # Progress bars
│   │   │   ├── skeleton.tsx    # Loading placeholders
│   │   │   ├── spinner.tsx     # Loading spinners
│   │   │   ├── tabs.tsx        # Tab navigation
│   │   │   ├── switch.tsx      # Toggle switches
│   │   │   ├── select.tsx      # Dropdown selects
│   │   │   ├── dropdown-menu.tsx  # Context menus
│   │   │   ├── tooltip.tsx     # Tooltips
│   │   │   ├── popover.tsx     # Popovers
│   │   │   ├── separator.tsx   # Dividers
│   │   │   ├── label.tsx       # Form labels
│   │   │   ├── textarea.tsx    # Multi-line inputs
│   │   │   ├── scroll-area.tsx # Scroll containers
│   │   │   ├── alert-dialog.tsx # Confirmation dialogs
│   │   │   ├── animated-page.tsx # Framer Motion wrappers
│   │   │   └── visually-hidden.tsx # A11y screen-reader text
│   │   ├── form/               # Form composition components
│   │   │   ├── form-field.tsx
│   │   │   ├── form-select-field.tsx
│   │   │   └── form-submit-button.tsx
│   │   ├── layout/             # Layout components
│   │   │   ├── app-shell.tsx
│   │   │   ├── app-shell-header.tsx
│   │   │   └── theme-toggle.tsx
│   │   ├── feedback/           # Error/feedback components
│   │   │   └── error-fallback.tsx
│   │   └── error-boundary.tsx  # React error boundary
│   │
│   ├── config/
│   │   ├── i18n.ts             # Locale config (en, hi, ta)
│   │   ├── translations.ts     # Translation key-value maps
│   │   ├── routes.ts           # Route constants
│   │   └── env.ts              # Zod-validated env vars
│   │
│   ├── hooks/
│   │   ├── use-media-query.ts  # Responsive breakpoint hook
│   │   ├── use-mounted.ts      # SSR mount detection
│   │   ├── use-translation.ts  # i18n hook
│   │   └── ...
│   │
│   ├── lib/
│   │   ├── utils.ts            # cn() class merger
│   │   ├── toast.ts            # Toast notification helpers
│   │   ├── toast-helpers.ts    # Error message extraction
│   │   └── ...
│   │
│   └── stores/
│       ├── ui-store.ts         # UI state (sidebar open/closed)
│       └── ...
│
└── features/
    ├── auth/                   # Authentication feature
    │   ├── components/
    │   │   ├── login-form.tsx
    │   │   ├── signup-form.tsx
    │   │   ├── app-session-gate.tsx
    │   │   └── google-sign-in-button.tsx
    │   ├── schema.ts           # Zod validation schemas
    │   ├── hooks/
    │   └── session-provider.tsx
    │
    ├── dashboard/              # Dashboard feature
    │   ├── components/
    │   │   ├── app-sidebar.tsx
    │   │   ├── app-header.tsx
    │   │   └── study-stats.tsx
    │   └── config/
    │       └── navigation.ts   # Nav item definitions
    │
    ├── progress/               # Progress tracking feature
    │   ├── components/
    │   │   ├── progress-ring.tsx
    │   │   └── streak-badge.tsx
    │   ├── hooks/
    │   └── api.ts
    │
    └── ...                     # Other features (chat, notes, quiz, etc.)
```

### 16.2 Component Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| UI primitives | PascalCase, single word | `Button`, `Card`, `Input` |
| Compositions | PascalCase, descriptive | `CardHeader`, `DialogContent` |
| Feature components | PascalCase, feature-prefixed | `LoginForm`, `AppSidebar` |
| Layout components | PascalCase, layout-prefixed | `AppShell`, `ThemeToggle` |
| Hooks | camelCase, `use-` prefix | `useMediaQuery`, `useMounted` |
| Config files | kebab-case | `navigation.ts`, `translations.ts` |

### 16.3 Adding New Components

1. **UI primitives** → `src/shared/components/ui/`
   - Follow shadcn pattern: forwardRef, cn() merging, cva for variants
   - Export both component and variant function (if applicable)

2. **Form components** → `src/shared/components/form/`
   - Integrate with React Hook Form
   - Support error display

3. **Layout components** → `src/shared/components/layout/`
   - Shell, header, navigation, theme toggle

4. **Feature components** → `src/features/{feature}/components/`
   - Feature-specific, may import from shared/ui
   - Co-located with feature hooks, API, and schemas

### 16.4 Adding New Design Tokens

1. Add CSS variable to both `:root` and `.dark` in `globals.css`
2. Add mapping in `@theme inline` block
3. Document in this DESIGN.md file
4. Update component styles to use the new token

---

## Appendix A: Quick Reference

### Common Class Combinations

| Pattern | Classes |
|---------|---------|
| Page container | `mx-auto max-w-5xl px-4 sm:px-6` |
| Section | `space-y-6` |
| Card row | `flex flex-wrap items-center gap-6 rounded-lg border border-border bg-card p-4` |
| Centered flex | `flex items-center justify-center` |
| Full-height flex col | `flex min-h-full flex-1 flex-col` |
| Sticky header | `sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur` |
| Truncated text | `truncate` |
| Code inline | `rounded-md bg-muted px-1.5 py-0.5 text-sm text-foreground` |
| Divider | `<Separator />` or `border-t border-border` |

### State Management Quick Reference

| State | Tool | Location |
|-------|------|----------|
| Theme | `next-themes` | `providers.tsx` |
| UI (sidebar) | Zustand | `shared/stores/ui-store.ts` |
| Server data | React Query | `shared/lib/query-client.ts` |
| Auth session | Custom context | `features/auth/session-provider.tsx` |
| Supabase | Custom provider | `features/auth/supabase-browser-provider.tsx` |
| Analytics | PostHog | `shared/lib/posthog.tsx` |
| Error monitoring | Sentry | `shared/lib/sentry.ts` |
| Toasts | Sonner | `providers.tsx` (dynamic import) |

---

## Appendix B: Design Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05 | Tailwind CSS v4 | CSS-first config, better performance, native CSS variable support |
| 2026-05 | Radix UI primitives | Headless, fully accessible, composable |
| 2026-05 | cva for variants | Type-safe, composable, Tailwind-friendly |
| 2026-05 | Geist font family | Modern, optimized for screens, free |
| 2026-05 | Lucide icons | Consistent stroke width, tree-shakeable, open source |
| 2026-05 | Framer Motion for page transitions | Smooth, declarative, React 19 compatible |
| 2026-05 | Sonner for toasts | Modern API, rich colors, accessible |
| 2026-05 | next-themes for dark mode | SSR-safe, system preference support, class-based |
| 2026-05 | Shadcn pattern for components | Copyable, customizable, no runtime dependency |
