import { getExams, getChapters } from "@/server/syllabus/get-chapters";
import { ChapterList } from "@/features/syllabus/components/chapter-list";
import { StudyStats } from "@/features/dashboard/components/study-stats";
import { QuickActions } from "@/features/dashboard/components/quick-actions";
import { getDashboardShellContext } from "@/features/dashboard/data/shell-context";

/**
 * Async RSC shell — static structure + server-resolved context. Interactive widgets
 * should live in separate `use client` islands imported here.
 */
export async function DashboardShell() {
  const ctx = await getDashboardShellContext();
  const exams = await getExams();

  // Get first exam (NEET 2026) and its chapters
  const defaultExam = exams[0];
  const chapters = defaultExam ? await getChapters(defaultExam.id) : [];

  // Compute aggregate stats
  const totalChapters = chapters.length;
  const totalSubtopics = chapters.reduce(
    (sum, ch) => sum + ch.topics.reduce((s, t) => s + t.subtopics.length, 0),
    0,
  );

  // TODO: Fetch actual completed counts from DB when auth is wired in RSC
  const chaptersCompleted = 0;
  const subtopicsCompleted = 0;
  const examProgress = totalSubtopics > 0 ? (subtopicsCompleted / totalSubtopics) * 100 : 0;

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">Dashboard</h1>
        <p className="text-sm leading-relaxed text-muted-foreground">
          Welcome to {ctx.appName}. Start learning with the syllabus below.
        </p>
      </header>

      {defaultExam && (
        <div className="space-y-4">
          <StudyStats
            examProgress={examProgress}
            chaptersCompleted={chaptersCompleted}
            totalChapters={totalChapters}
            subtopicsCompleted={subtopicsCompleted}
            totalSubtopics={totalSubtopics}
          />

          <QuickActions />

          <div>
            <h2 className="text-lg font-semibold text-foreground">{defaultExam.title}</h2>
            {defaultExam.description && (
              <p className="text-sm text-muted-foreground">{defaultExam.description}</p>
            )}
          </div>

          <ChapterList chapters={chapters} />
        </div>
      )}

      {!defaultExam && (
        <div className="rounded-lg border border-dashed border-border bg-card/50 px-4 py-8 text-center">
          <p className="text-sm text-muted-foreground">No exams available</p>
        </div>
      )}
    </div>
  );
}
