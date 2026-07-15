import * as React from "react";
import type { FieldValues } from "react-hook-form";
import { useFormContext } from "react-hook-form";
import { Label } from "@/shared/components/ui/label";
import { cn } from "@/shared/lib/utils";

interface FormFieldProps<T extends FieldValues>
  extends React.HTMLAttributes<HTMLDivElement> {
  name: keyof T | string;
  label: string;
  hint?: string;
  error?: string;
  children: React.ReactNode;
}

export function FormField<T extends FieldValues>({
  name,
  label,
  hint,
  error,
  children,
  className,
}: FormFieldProps<T>) {
  const { formState } = useFormContext<T>();
  const fieldError = error ?? (formState.errors[name] as { message?: string } | undefined)?.message;

  return (
    <div className={cn("space-y-2", className)}>
      <Label htmlFor={name as string}>
        {label}
        {hint && (
          <span className="ml-1 text-xs font-normal text-muted-foreground">
            {hint}
          </span>
        )}
      </Label>
      {children}
      {fieldError && (
        <p className="text-sm text-destructive">{fieldError}</p>
      )}
    </div>
  );
}
