import type { Metadata } from "next";
import { getChapterDetail } from "@/server/syllabus/get-chapters";
import { ChatWindow } from "@/features/chat/components/chat-window";
import { ChapterDetailClient } from "@/features/syllabus/components/chapter-detail";
import { Button } from "@/shared/components/ui/button";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export const metadata: Metadata = {
  title: "Chapter Detail",
};

interface ChapterDetailPageProps {
  params: Promise<{ chapterId: string }>;
}

export default async function ChapterDetailPage({ params }: ChapterDetailPageProps) {
  const { chapterId } = await params;
  const chapter = await getChapterDetail(chapterId);

  if (!chapter) {
    return (
      <div className="space-y-6 p-6">
        <div className="rounded-lg border border-dashed border-border bg-card/50 px-4 py-8 text-center">
          <p className="text-sm text-muted-foreground">Chapter not found</p>
          <Button asChild variant="outline" className="mt-4">
            <Link href="/syllabus">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to syllabus
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  const totalSubtopics = chapter.topics.reduce(
    (sum, t) => sum + t.subtopics.length,
    0,
  );

  return (
    <div className="flex h-[calc(100vh-3.5rem)]">
      <div className="w-96 flex-shrink-0 overflow-y-auto border-r border-border p-6">
        <Button asChild variant="ghost" size="sm" className="mb-4">
          <Link href="/syllabus">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Link>
        </Button>

        <ChapterDetailClient
          chapterName={chapter.name}
          topics={chapter.topics}
          totalSubtopics={totalSubtopics}
        />
      </div>

      <div className="flex-1">
        <ChatWindow
          sessionId=""
          chapterContext={chapter.name}
        />
      </div>
    </div>
  );
}
