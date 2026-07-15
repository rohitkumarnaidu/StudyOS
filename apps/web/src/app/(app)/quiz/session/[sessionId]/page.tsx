import type { Metadata } from "next";
import { getQuizResult } from "@/server/quiz/get-quiz";
import { QuizResults } from "@/features/quiz/components/quiz-results";
import { Button } from "@/shared/components/ui/button";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export const metadata: Metadata = {
  title: "Quiz Session",
};

interface QuizSessionPageProps {
  params: Promise<{ sessionId: string }>;
}

export default async function QuizSessionPage({ params }: QuizSessionPageProps) {
  const { sessionId } = await params;
  const result = await getQuizResult(sessionId);

  if (!result) {
    return (
      <div className="space-y-6 p-6">
        <div className="rounded-lg border border-dashed border-border bg-card/50 px-4 py-8 text-center">
          <p className="text-sm text-muted-foreground">Quiz session not found</p>
          <Button asChild variant="outline" className="mt-4">
            <Link href="/quiz">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Quiz
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  return <QuizResults result={result} />;
}
