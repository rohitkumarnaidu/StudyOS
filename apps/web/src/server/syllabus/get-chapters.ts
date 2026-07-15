"use server";

import { apiFetch } from "@/shared/api";

export interface SubtopicData {
  id: string;
  name: string;
  sort_order: number;
  estimated_minutes: number | null;
}

export interface TopicData {
  id: string;
  name: string;
  sort_order: number;
  subtopics: SubtopicData[];
}

export interface ChapterData {
  id: string;
  name: string;
  sort_order: number;
  topics: TopicData[];
}

export interface ExamData {
  id: string;
  code: string;
  title: string;
  description: string | null;
}

export async function getExams(): Promise<ExamData[]> {
  try {
    const response = await apiFetch<ExamData[]>("/v1/syllabus/exams");
    return response || [];
  } catch (error) {
    console.error("Failed to fetch exams:", error);
    return [];
  }
}

export async function getChapters(
  examId?: string,
  subjectId?: string
): Promise<ChapterData[]> {
  try {
    const params = new URLSearchParams();
    if (examId) params.append("exam_id", examId);
    if (subjectId) params.append("subject_id", subjectId);

    const url = `/v1/syllabus/chapters${params.toString() ? `?${params.toString()}` : ""}`;
    const response = await apiFetch<ChapterData[]>(url);
    return response || [];
  } catch (error) {
    console.error("Failed to fetch chapters:", error);
    return [];
  }
}

export async function getChapterDetail(chapterId: string): Promise<ChapterData | null> {
  try {
    const response = await apiFetch<ChapterData>(`/v1/syllabus/chapters/${chapterId}`);
    return response || null;
  } catch (error) {
    console.error("Failed to fetch chapter detail:", error);
    return null;
  }
}
