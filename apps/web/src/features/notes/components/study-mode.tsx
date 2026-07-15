"use client";

import { useState } from "react";
import { PDFViewer } from "@/features/notes/components/pdf-viewer";
import { HighlightsManager } from "@/features/notes/components/highlights-manager";
import { PersonalNotes } from "@/features/notes/components/personal-notes";
import { Bookmarks } from "@/features/notes/components/bookmarks";
import { Button } from "@/shared/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { Maximize2, Minimize2, Highlighter, StickyNote, Bookmark } from "lucide-react";

interface StudyModeProps {
  noteId: string;
  pdfUrl: string;
  title: string;
  pageCount: number;
}

export function StudyMode({ noteId, pdfUrl, title, pageCount }: StudyModeProps) {
  const [fullScreen, setFullScreen] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars -- reserved for future page navigation
  const [currentPage, setCurrentPage] = useState(1);

  if (fullScreen) {
    return (
      <div className="fixed inset-0 z-50 bg-background">
        <div className="flex h-full">
          <div className="flex-1">
            <PDFViewer url={pdfUrl} title={title} pageCount={pageCount} />
          </div>
          <div className="w-80 border-l border-border overflow-auto p-4 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold">Study Tools</h2>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setFullScreen(false)}
                aria-label="Exit fullscreen"
              >
                <Minimize2 className="h-4 w-4" />
              </Button>
            </div>
            <HighlightsManager noteId={noteId} />
            <PersonalNotes noteId={noteId} pageNumber={currentPage} />
            <Bookmarks noteId={noteId} currentPage={currentPage} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{title}</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setFullScreen(true)}
        >
          <Maximize2 className="mr-2 h-4 w-4" />
          Study Mode
        </Button>
      </div>

      <div className="h-[600px] rounded-lg border border-border overflow-hidden">
        <PDFViewer url={pdfUrl} title={title} pageCount={pageCount} />
      </div>

      <Tabs defaultValue="highlights">
        <TabsList>
          <TabsTrigger value="highlights" className="flex items-center gap-2">
            <Highlighter className="h-4 w-4" />
            Highlights
          </TabsTrigger>
          <TabsTrigger value="notes" className="flex items-center gap-2">
            <StickyNote className="h-4 w-4" />
            Notes
          </TabsTrigger>
          <TabsTrigger value="bookmarks" className="flex items-center gap-2">
            <Bookmark className="h-4 w-4" />
            Bookmarks
          </TabsTrigger>
        </TabsList>

        <TabsContent value="highlights" className="mt-4">
          <HighlightsManager noteId={noteId} />
        </TabsContent>

        <TabsContent value="notes" className="mt-4">
          <PersonalNotes noteId={noteId} />
        </TabsContent>

        <TabsContent value="bookmarks" className="mt-4">
          <Bookmarks noteId={noteId} currentPage={currentPage} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
