import * as React from "react";
import { Controller, useFormContext } from "react-hook-form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/shared/components/ui/select";
import { Label } from "@/shared/components/ui/label";
import { cn } from "@/shared/lib/utils";

interface FormSelectFieldProps {
  name: string;
  label: string;
  placeholder?: string;
  options: { value: string; label: string }[];
  description?: string;
  disabled?: boolean;
  className?: string;
}

export function FormSelectField({
  name,
  label,
  placeholder = "Select...",
  options,
  description,
  disabled,
  className,
}: FormSelectFieldProps) {
  const { control, formState } = useFormContext();
  const error = formState.errors[name];

  return (
    <div className={cn("space-y-2", className)}>
      <Label htmlFor={name}>
        {label}
        {description && (
          <span className="ml-1 text-xs font-normal text-muted-foreground">
            {description}
          </span>
        )}
      </Label>
      <Controller
        name={name}
        control={control}
        render={({ field }) => (
          <Select
            onValueChange={field.onChange}
            defaultValue={field.value}
            disabled={disabled}
          >
            <SelectTrigger id={name} className={error ? "border-destructive" : ""}>
              <SelectValue placeholder={placeholder} />
            </SelectTrigger>
            <SelectContent>
              {options.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      />
      {error && typeof error.message === "string" && (
        <p className="text-sm text-destructive">{error.message}</p>
      )}
    </div>
  );
}
