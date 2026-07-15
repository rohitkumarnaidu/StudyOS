import type { HTMLAttributes } from "react";
import { cn } from "@/shared/lib";

/**
 * Screen-reader-only text (visually hidden, still announced by assistive tech).
 */
export function VisuallyHidden({ className, ...props }: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "absolute h-px w-px overflow-hidden whitespace-nowrap border-0 p-0 [clip:rect(0,0,0,0)]",
        className,
      )}
      {...props}
    />
  );
}
