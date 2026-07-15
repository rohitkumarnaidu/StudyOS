import { create } from "zustand";

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

interface SyllabusState {
  exams: ExamData[];
  selectedExamId: string | null;
  expandedChapters: Set<string>;
  completedSubtopics: Set<string>;
  setExams: (exams: ExamData[]) => void;
  setSelectedExamId: (id: string | null) => void;
  toggleChapter: (id: string) => void;
  toggleSubtopic: (id: string) => void;
  reset: () => void;
}

export const useSyllabusStore = create<SyllabusState>((set) => ({
  exams: [],
  selectedExamId: null,
  expandedChapters: new Set(),
  completedSubtopics: new Set(),
  setExams: (exams) => set({ exams }),
  setSelectedExamId: (id) => set({ selectedExamId: id }),
  toggleChapter: (id) =>
    set((state) => {
      const next = new Set(state.expandedChapters);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return { expandedChapters: next };
    }),
  toggleSubtopic: (id) =>
    set((state) => {
      const next = new Set(state.completedSubtopics);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return { completedSubtopics: next };
    }),
  reset: () =>
    set({
      exams: [],
      selectedExamId: null,
      expandedChapters: new Set(),
      completedSubtopics: new Set(),
    }),
}));
