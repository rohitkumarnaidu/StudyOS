import type { Metadata } from "next";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Syllabus",
};

import { getExams, getChapters } from "@/server/syllabus/get-chapters";
import { ChapterList } from "@/features/syllabus/components/chapter-list";

export default function SyllabusPage() {
  return <SyllabusContent />;
}

async function SyllabusContent() {
  try {
    const exams = await getExams();
    const defaultExam = exams[0];
    const chapters = defaultExam ? await getChapters(defaultExam.id) : [];

    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Syllabus</h1>
          <p className="text-sm text-muted-foreground">
            Browse and track your NEET 2026 syllabus progress.
          </p>
        </div>

        {defaultExam && (
          <div>
            <h2 className="text-lg font-semibold text-foreground mb-4">{defaultExam.title}</h2>
            <ChapterList chapters={chapters} />
          </div>
        )}
      </div>
    );
  } catch (err) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-semibold tracking-tight">Syllabus</h1>
        <p className="text-sm text-muted-foreground">Browse and track your NEET 2026 syllabus progress.</p>
      </div>
    );
  }
}
