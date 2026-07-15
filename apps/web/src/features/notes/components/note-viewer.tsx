"use client";

import { useState } from "react";
import type { NoteData } from "@/features/notes/api";
import { PDFViewer } from "@/features/notes/components/pdf-viewer";
import { MindMapViewer } from "@/features/notes/components/mindmap-viewer";
import { StructuredNotes } from "@/features/notes/components/structured-notes";
import { HighlightsManager } from "@/features/notes/components/highlights-manager";
import { PersonalNotes } from "@/features/notes/components/personal-notes";
import { DownloadDialog } from "@/features/notes/components/download-dialog";
import { Button } from "@/shared/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { ArrowLeft, FileText, Brain, ListTree } from "lucide-react";
import Link from "next/link";

interface NoteViewerProps {
  note: NoteData;
}

export function NoteViewer({ note }: NoteViewerProps) {
  const [activeTab, setActiveTab] = useState("pdf");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button asChild variant="ghost" size="sm">
            <Link href="/notes">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Link>
          </Button>
          <div>
            <h1 className="text-xl font-semibold">{note.title}</h1>
            <p className="text-sm text-muted-foreground">
              {note.page_count} pages • {note.note_type.toUpperCase()}
            </p>
          </div>
        </div>

        <DownloadDialog
          noteId={note.id}
          noteTitle={note.title}
          hasMindmap={note.note_type === "mindmap"}
        />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="pdf" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            PDF
          </TabsTrigger>
          <TabsTrigger value="structured" className="flex items-center gap-2">
            <ListTree className="h-4 w-4" />
            Structured
          </TabsTrigger>
          {note.note_type === "mindmap" && (
            <TabsTrigger value="mindmap" className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Mind Map
            </TabsTrigger>
          )}
        </TabsList>

        <TabsContent value="pdf" className="mt-4">
          <div className="h-[70vh] rounded-lg border border-border overflow-hidden">
            {note.status === "ready" ? (
              <PDFViewer
                url={`/api/notes/${note.id}/file`}
                title={note.title}
                pageCount={note.page_count}
              />
            ) : (
              <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                {note.status === "processing"
                  ? "Processing your PDF..."
                  : "Note not ready"}
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="structured" className="mt-4">
          <div className="rounded-lg border border-border bg-card p-4">
            {note.summary ? (
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-semibold mb-2">Summary</h3>
                  <p className="text-sm text-muted-foreground">{note.summary}</p>
                </div>
                <StructuredNotes
                  data={[
                    {
                      id: "root",
                      title: note.title,
                      content: note.summary,
                      children: note.tags.map((tag, i) => ({
                        id: `tag-${i}`,
                        title: tag,
                      })),
                    },
                  ]}
                />
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-8">
                Structured content will appear after processing
              </p>
            )}
          </div>
        </TabsContent>

        {note.note_type === "mindmap" && (
          <TabsContent value="mindmap" className="mt-4">
            <div className="h-[70vh] rounded-lg border border-border overflow-hidden">
              <MindMapViewer
                data={{
                  id: "root",
                  label: note.title,
                  children: note.tags.map((tag, i) => ({
                    id: `tag-${i}`,
                    label: tag,
                  })),
                }}
              />
            </div>
          </TabsContent>
        )}
      </Tabs>

      <div className="grid gap-4 md:grid-cols-2">
        <HighlightsManager noteId={note.id} />
        <PersonalNotes noteId={note.id} />
      </div>
    </div>
  );
}
