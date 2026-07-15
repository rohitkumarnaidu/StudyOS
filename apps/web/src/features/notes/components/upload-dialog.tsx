"use client";

import { useState, useCallback } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/shared/components/ui/dialog";
import { Button } from "@/shared/components/ui/button";
import { Upload, X, FileText } from "lucide-react";
import { cn } from "@/shared/lib";
import { notifySuccess } from "@/shared/lib";

interface UploadDialogProps {
  onUploadComplete?: () => void;
}

interface UploadItem {
  id: string;
  file: File;
  progress: number;
  status: "pending" | "uploading" | "done" | "error";
}

export function UploadDialog({ onUploadComplete }: UploadDialogProps) {
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<UploadItem[]>([]);
  const [dragging, setDragging] = useState(false);

  const uploadFiles = useCallback(async (uploadItems: UploadItem[]) => {
    for (const item of uploadItems) {
      setItems((prev) =>
        prev.map((i) => (i.id === item.id ? { ...i, status: "uploading" } : i)),
      );

      try {
        const formData = new FormData();
        formData.append("file", item.file);

        await new Promise((resolve) => setTimeout(resolve, 1000 + Math.random() * 2000));

        setItems((prev) =>
          prev.map((i) => (i.id === item.id ? { ...i, progress: 100, status: "done" } : i)),
        );
      } catch {
        setItems((prev) =>
          prev.map((i) => (i.id === item.id ? { ...i, status: "error" } : i)),
        );
      }
    }

    const allDone = uploadItems.every((i) => i.status === "done");
    if (allDone) {
      notifySuccess(`${uploadItems.length} file(s) uploaded`);
      onUploadComplete?.();
    }
  }, [onUploadComplete]);

  const handleFiles = useCallback((files: FileList | File[]) => {
    const newItems: UploadItem[] = Array.from(files).map((file) => ({
      id: crypto.randomUUID(),
      file,
      progress: 0,
      status: "pending",
    }));
    setItems((prev) => [...prev, ...newItems]);
    void uploadFiles(newItems);
  }, [uploadFiles]);

  function removeItem(id: string) {
    setItems((prev) => prev.filter((i) => i.id !== id));
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <Upload className="mr-2 h-4 w-4" />
          Upload
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Upload PDF Notes</DialogTitle>
        </DialogHeader>

        <div
          className={cn(
            "flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors",
            dragging
              ? "border-primary bg-primary/5"
              : "border-border hover:border-primary/50",
          )}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            handleFiles(e.dataTransfer.files);
          }}
        >
          <FileText className="mb-2 h-8 w-8 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            Drag and drop PDF files here, or
          </p>
          <Button
            variant="outline"
            size="sm"
            className="mt-2"
            onClick={() => {
              const input = document.createElement("input");
              input.type = "file";
              input.accept = ".pdf";
              input.multiple = true;
              input.onchange = () => {
                if (input.files) handleFiles(input.files);
              };
              input.click();
            }}
          >
            Browse files
          </Button>
        </div>

        {items.length > 0 && (
          <div className="mt-4 space-y-2 max-h-48 overflow-auto">
            {items.map((item) => (
              <div
                key={item.id}
                className="flex items-center gap-3 rounded-md border border-border px-3 py-2"
              >
                <FileText className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
                <div className="flex-1 min-w-0">
                  <p className="truncate text-sm">{item.file.name}</p>
                  <div className="mt-1 h-1 w-full overflow-hidden rounded-full bg-muted">
                    <div
                      className={cn(
                        "h-full rounded-full transition-all",
                        item.status === "done"
                          ? "bg-emerald-500 w-full"
                          : item.status === "error"
                            ? "bg-destructive w-full"
                            : "bg-primary animate-pulse",
                        item.status === "uploading" && "w-1/2",
                      )}
                    />
                  </div>
                </div>
                <button
                  onClick={() => removeItem(item.id)}
                  className="flex-shrink-0 text-muted-foreground hover:text-foreground"
                  aria-label={`Remove ${item.file.name}`}
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
