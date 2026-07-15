/* eslint-disable react-hooks/incompatible-library -- RHF watch() is required for conditional UI */
"use client";

import { useState, useCallback } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { FormProvider, useForm } from "react-hook-form";
import { z } from "zod";
import { FormField } from "@/shared/components/form/form-field";
import { Button } from "@/shared/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { Input } from "@/shared/components/ui/input";
import { createQuizSession, type CreateQuizRequest } from "@/features/quiz/api";
import { notifyError } from "@/shared/lib";
import { useRouter } from "next/navigation";

const quizSetupSchema = z.object({
  question_count: z.coerce.number().min(5).max(180),
  quiz_type: z.enum(["practice", "timed", "mock"]),
  time_limit_minutes: z.coerce.number().min(1).max(240).optional(),
  difficulty: z.coerce.number().min(1).max(5).optional(),
  chapter_id: z.string().optional(),
});

type QuizSetupValues = z.infer<typeof quizSetupSchema>;

interface QuizSetupProps {
  chapterId?: string;
  chapterName?: string;
}

export function QuizSetup({ chapterId, chapterName }: QuizSetupProps) {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);

  const form = useForm<QuizSetupValues>({
    resolver: zodResolver(quizSetupSchema),
    defaultValues: {
      question_count: 30,
      quiz_type: "practice",
      time_limit_minutes: 60,
      difficulty: 2,
      chapter_id: chapterId,
    },
  });

  const quizType = form.watch("quiz_type");

  const onSubmit = useCallback(
    async (values: QuizSetupValues) => {
      setSubmitting(true);
      try {
        const body: CreateQuizRequest = {
          chapter_id: values.chapter_id || undefined,
          question_count: values.question_count,
          quiz_type: values.quiz_type,
          time_limit_minutes: values.quiz_type !== "practice" ? values.time_limit_minutes : undefined,
          difficulty: values.difficulty,
        };
        const session = await createQuizSession(body);
        router.push(`/quiz/session/${session.id}`);
      } catch {
        notifyError("Failed to create quiz session");
      } finally {
        setSubmitting(false);
      }
    },
    [router],
  );

  return (
    <FormProvider {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 max-w-lg">
        <div>
          <h2 className="text-lg font-semibold">
            {chapterName ? `Quiz: ${chapterName}` : "Practice Quiz"}
          </h2>
          <p className="text-sm text-muted-foreground">
            Configure your quiz settings below.
          </p>
        </div>

        <FormField<QuizSetupValues> name="quiz_type" label="Quiz Type">
          <Select
            value={form.watch("quiz_type")}
            onValueChange={(v) => form.setValue("quiz_type", v as QuizSetupValues["quiz_type"])}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="practice">Practice (no timer)</SelectItem>
              <SelectItem value="timed">Timed Quiz</SelectItem>
              <SelectItem value="mock">Mock Test (180Q / 3hr)</SelectItem>
            </SelectContent>
          </Select>
        </FormField>

        <FormField<QuizSetupValues> name="question_count" label="Number of Questions">
          <Input type="number" min={5} max={180} {...form.register("question_count")} />
        </FormField>

        {quizType !== "practice" && (
          <FormField<QuizSetupValues> name="time_limit_minutes" label="Time Limit (minutes)">
            <Input type="number" min={1} max={240} {...form.register("time_limit_minutes")} />
          </FormField>
        )}

        <FormField<QuizSetupValues> name="difficulty" label="Difficulty (1-5)">
          <Input type="number" min={1} max={5} {...form.register("difficulty")} />
        </FormField>

        <Button type="submit" className="w-full" disabled={submitting}>
          {submitting ? "Creating..." : "Start Quiz"}
        </Button>
      </form>
    </FormProvider>
  );
}
