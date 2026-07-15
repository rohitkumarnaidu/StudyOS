import Dexie, { type Table } from "dexie";

export interface SyllabusChapter {
  id: string;
  name: string;
  sort_order: number;
  topics: Array<{
    id: string;
    name: string;
    sort_order: number;
    subtopics: Array<{
      id: string;
      name: string;
      sort_order: number;
      estimated_minutes: number | null;
    }>;
  }>;
  cached_at: number;
}

export interface SubtopicCompletion {
  subtopic_id: string;
  completed: boolean;
  synced: boolean;
  timestamp: number;
}

export interface SyncQueueItem {
  id?: number;
  subtopic_id: string;
  action: "toggle";
  timestamp: number;
  attempts: number;
}

export class StudyOSDB extends Dexie {
  chapters!: Table<SyllabusChapter, string>;
  completions!: Table<SubtopicCompletion, string>;
  syncQueue!: Table<SyncQueueItem, number>;

  constructor() {
    super("StudyOSDB");
    this.version(1).stores({
      chapters: "id, cached_at",
      completions: "subtopic_id, synced, timestamp",
      syncQueue: "++id, subtopic_id, timestamp, attempts",
    });
  }
}

export const db = new StudyOSDB();
