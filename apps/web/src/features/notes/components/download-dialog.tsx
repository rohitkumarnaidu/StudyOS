"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/shared/components/ui/dialog";
import { Button } from "@/shared/components/ui/button";
import { Download, FileDown, Image, FileText as FileTextIcon, Archive } from "lucide-react";
import { notifySuccess, notifyError } from "@/shared/lib";

interface DownloadDialogProps {
  noteId: string;
  noteTitle: string;
  hasMindmap: boolean;
}

type DownloadOption = {
  id: string;
  label: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  action: () => Promise<void>;
};

export function DownloadDialog({ noteId, noteTitle, hasMindmap }: DownloadDialogProps) {
  const [open, setOpen] = useState(false);
  const [downloading, setDownloading] = useState<string | null>(null);

  const options: DownloadOption[] = [
    {
      id: "original",
      label: "Original PDF",
      description: "Download the uploaded PDF file",
      icon: FileTextIcon,
      action: async () => {
        window.open(`/api/notes/${noteId}/download?type=original`, "_blank");
      },
    },
    {
      id: "summary",
      label: "Summary PDF",
      description: "AI-generated summary of the note",
      icon: FileDown,
      action: async () => {
        window.open(`/api/notes/${noteId}/download?type=summary`, "_blank");
      },
    },
    ...(hasMindmap
      ? [
          {
            id: "mindmap" as const,
            label: "Mind Map Image",
            description: "Export mind map as PNG",
            icon: Image,
            action: async () => {
              window.open(`/api/notes/${noteId}/download?type=mindmap`, "_blank");
            },
          } as DownloadOption,
        ]
      : []),
    {
      id: "highlights",
      label: "Highlights",
      description: "Export all highlights as text",
      icon: FileTextIcon,
      action: async () => {
        window.open(`/api/notes/${noteId}/download?type=highlights`, "_blank");
      },
    },
    {
      id: "bulk",
      label: "Bulk ZIP",
      description: "Download all notes as ZIP archive",
      icon: Archive,
      action: async () => {
        window.open("/api/notes/download-all", "_blank");
      },
    },
  ];

  async function handleDownload(option: DownloadOption) {
    setDownloading(option.id);
    try {
      await option.action();
      notifySuccess(`Downloading ${option.label}`);
    } catch {
      notifyError(`Failed to download ${option.label}`);
    } finally {
      setDownloading(null);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Download className="mr-2 h-4 w-4" />
          Download
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Download {noteTitle}</DialogTitle>
        </DialogHeader>

        <div className="space-y-2 mt-2">
          {options.map((option) => {
            const Icon = option.icon;
            return (
              <button
                key={option.id}
                className="flex w-full items-center gap-3 rounded-lg border border-border p-3 text-left hover:bg-muted/50 transition-colors disabled:opacity-50"
                onClick={() => void handleDownload(option)}
                disabled={downloading !== null}
              >
                <Icon className="h-5 w-5 flex-shrink-0 text-muted-foreground" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium">{option.label}</p>
                  <p className="text-xs text-muted-foreground">{option.description}</p>
                </div>
                {downloading === option.id && (
                  <span className="text-xs text-muted-foreground">Downloading...</span>
                )}
              </button>
            );
          })}
        </div>
      </DialogContent>
    </Dialog>
  );
}
