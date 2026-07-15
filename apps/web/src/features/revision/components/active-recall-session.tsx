"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { Textarea } from "@/shared/components/ui/textarea";
import { Progress } from "@/shared/components/ui/progress";
import {
  useCreateActiveRecallSession,
  useActiveRecallSession,
  useSubmitActiveRecallAnswer,
} from "@/features/revision/hooks/use-revision";

export function ActiveRecallSession() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [answer, setAnswer] = useState("");
  const [showAnswer, setShowAnswer] = useState(false);

  const createMutation = useCreateActiveRecallSession();
  const { data: session } = useActiveRecallSession(sessionId);
  const submitMutation = useSubmitActiveRecallAnswer();

  const handleStart = () => {
    createMutation.mutate({ maxQuestions: 10 }, {
      onSuccess: (data) => {
        setSessionId(data.session_id);
        setAnswer("");
        setShowAnswer(false);
      },
    });
  };

  const handleSubmit = () => {
    if (!session || !session.questions[session.current_index]) return;
    const q = session.questions[session.current_index];
    submitMutation.mutate({
      sessionId: session.session_id,
      questionId: q.question_id,
      answer,
    });
    setAnswer("");
    setShowAnswer(false);
  };

  if (!session) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Active Recall Session</CardTitle>
          <CardDescription>Test your memory with guided questions</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={handleStart} disabled={createMutation.isPending} className="w-full">
            {createMutation.isPending ? "Starting..." : "Start Session"}
          </Button>
        </CardContent>
      </Card>
    );
  }

  const currentQ = session.questions[session.current_index];
  const progressPct = session.questions.length > 0
    ? ((session.current_index) / session.questions.length) * 100
    : 0;

  if (session.completed) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Session Complete</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center">
            <p className="text-4xl font-bold">{session.score}/{session.questions.length}</p>
            <p className="text-muted-foreground">Correct Answers</p>
          </div>
          <Button onClick={handleStart} className="w-full">New Session</Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle>Question {session.current_index + 1}/{session.questions.length}</CardTitle>
          <span className="text-sm text-muted-foreground">Score: {session.score}</span>
        </div>
        <Progress value={progressPct} className="mt-2" />
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="p-4 bg-muted rounded-lg">
          <p className="font-medium">{currentQ?.question}</p>
        </div>

        {!showAnswer ? (
          <div className="space-y-3">
            <Textarea
              placeholder="Type your answer..."
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
            />
            <div className="flex gap-2">
              <Button onClick={() => setShowAnswer(true)} variant="outline" className="flex-1">
                Show Answer
              </Button>
              <Button onClick={handleSubmit} disabled={!answer.trim()} className="flex-1">
                Submit
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="p-4 bg-primary/10 rounded-lg">
              <p className="text-sm font-medium">Answer:</p>
              <p>{currentQ?.answer}</p>
            </div>
            <Button onClick={handleSubmit} className="w-full">
              Continue
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
