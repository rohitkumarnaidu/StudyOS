import type { Metadata } from "next";
import { NoteViewer } from "@/features/notes/components/note-viewer";
import { getNote } from "@/server/notes/get-note";
import { Button } from "@/shared/components/ui/button";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export const metadata: Metadata = {
  title: "Note Detail",
};

interface NoteDetailPageProps {
  params: Promise<{ noteId: string }>;
}

export default async function NoteDetailPage({ params }: NoteDetailPageProps) {
  const { noteId } = await params;
  const note = await getNote(noteId);

  if (!note) {
    return (
      <div className="space-y-6 p-6">
        <div className="rounded-lg border border-dashed border-border bg-card/50 px-4 py-8 text-center">
          <p className="text-sm text-muted-foreground">Note not found</p>
          <Button asChild variant="outline" className="mt-4">
            <Link href="/notes">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to notes
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  return <NoteViewer note={note} />;
}
