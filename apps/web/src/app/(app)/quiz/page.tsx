import type { Metadata } from "next";
import dynamic from "next/dynamic";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { Skeleton } from "@/shared/components/ui/skeleton";

// Lazy-load heavy quiz components
const QuizSetup = dynamic(
  () => import("@/features/quiz/components/quiz-setup").then((m) => ({ default: m.QuizSetup })),
  { loading: () => <Skeleton className="h-64 w-full" /> }
);

const MistakeLog = dynamic(
  () => import("@/features/quiz/components/mistake-log").then((m) => ({ default: m.MistakeLog })),
  { loading: () => <Skeleton className="h-64 w-full" /> }
);

export const metadata: Metadata = {
  title: "Quiz & Practice",
  description: "Test your knowledge with practice quizzes, timed tests, and full mock exams.",
};

export default function QuizPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Quiz & Practice</h1>
        <p className="text-sm text-muted-foreground">
          Test your knowledge with practice quizzes, timed tests, or full mock exams.
        </p>
      </div>

      <Tabs defaultValue="quiz">
        <TabsList>
          <TabsTrigger value="quiz">New Quiz</TabsTrigger>
          <TabsTrigger value="mistakes">Mistake Log</TabsTrigger>
        </TabsList>

        <TabsContent value="quiz" className="mt-6">
          <QuizSetup />
        </TabsContent>

        <TabsContent value="mistakes" className="mt-6">
          <MistakeLog />
        </TabsContent>
      </Tabs>
    </div>
  );
}
