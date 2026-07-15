import { apiFetch } from "@/shared/api";

export interface MistakeRecord {
  mistake_id: string;
  profile_id: string;
  question_id: string;
  mistake_type: string;
  concept_tags: string[];
  confidence_level: number;
  time_taken_seconds: number;
  timestamp: string;
}

export interface MistakeStats {
  total_mistakes: number;
  avg_confidence: number;
  avg_time_seconds: number;
  type_distribution: Record<string, number>;
  top_concepts: [string, number][];
}

export interface ConceptGap {
  concept: string;
  gap_score: number;
  mistake_count: number;
  last_mistake_timestamp: string;
  related_concepts: string[];
  recommended_action: string;
}

export interface MistakePrediction {
  concept: string;
  predicted_probability: number;
  risk_level: string;
  contributing_factors: string[];
  recommended_prevention: string;
}

export interface MistakeCluster {
  cluster_id: string;
  theme: string;
  mistake_count: number;
  common_concepts: string[];
  mistakes: Array<Record<string, unknown>>;
}

export interface StudyPlanItem {
  concept: string;
  priority: "high" | "medium" | "low";
  gap_score: number;
  action: string;
  related_concepts: string[];
}

export interface IntelligenceReport {
  mistake_stats: MistakeStats;
  knowledge_gaps: ConceptGap[];
  predictions: MistakePrediction[];
  clusters: MistakeCluster[];
  study_plan: StudyPlanItem[];
}

function buildQueryParams(params: Record<string, string | number | string[] | undefined>): string {
  const parts: string[] = [];
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined) continue;
    if (Array.isArray(value)) {
      for (const v of value) {
        parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(v)}`);
      }
    } else {
      parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`);
    }
  }
  return parts.length > 0 ? `?${parts.join("&")}` : "";
}

export async function logMistake(params: {
  question_id: string;
  mistake_type: string;
  concept_tags?: string[];
  confidence_level?: number;
  time_taken_seconds?: number;
}): Promise<MistakeRecord> {
  const query = buildQueryParams({
    question_id: params.question_id,
    mistake_type: params.mistake_type,
    concept_tags: params.concept_tags,
    confidence_level: params.confidence_level,
    time_taken_seconds: params.time_taken_seconds,
  });
  const response = await apiFetch<{ data: MistakeRecord }>(`/v1/mistake-intelligence/mistakes${query}`, {
    method: "POST",
  });
  return response.data;
}

export async function getMistakes(filters?: { mistake_type?: string; concept?: string }): Promise<{ mistakes: MistakeRecord[]; total: number }> {
  const query = buildQueryParams({
    mistake_type: filters?.mistake_type,
    concept: filters?.concept,
  });
  const response = await apiFetch<{ data: { mistakes: MistakeRecord[]; total: number } }>(`/v1/mistake-intelligence/mistakes${query}`);
  return response.data;
}

export async function getMistakeStats(): Promise<MistakeStats> {
  const response = await apiFetch<{ data: MistakeStats }>("/v1/mistake-intelligence/mistakes/stats");
  return response.data;
}

export async function analyzeGaps(minAttempts = 3): Promise<{ gaps: ConceptGap[]; total: number }> {
  const query = buildQueryParams({ min_attempts: minAttempts });
  const response = await apiFetch<{ data: { gaps: ConceptGap[]; total: number } }>(`/v1/mistake-intelligence/mistakes/gaps${query}`);
  return response.data;
}

export async function getWeakConcepts(topN = 5): Promise<{ weak_concepts: ConceptGap[] }> {
  const query = buildQueryParams({ top_n: topN });
  const response = await apiFetch<{ data: { weak_concepts: ConceptGap[] } }>(`/v1/mistake-intelligence/mistakes/weak-concepts${query}`);
  return response.data;
}

export async function getMasteryLevel(concept: string): Promise<{ concept: string; mastery_level: string }> {
  const response = await apiFetch<{ data: { concept: string; mastery_level: string } }>(`/v1/mistake-intelligence/mistakes/mastery/${concept}`);
  return response.data;
}

export async function getStudyPlan(maxConcepts = 5): Promise<{ study_plan: StudyPlanItem[] }> {
  const query = buildQueryParams({ max_concepts: maxConcepts });
  const response = await apiFetch<{ data: { study_plan: StudyPlanItem[] } }>(`/v1/mistake-intelligence/mistakes/study-plan${query}`);
  return response.data;
}

export async function getPredictions(concepts?: string[]): Promise<{ predictions: MistakePrediction[] }> {
  const query = concepts ? buildQueryParams({ concepts }) : "";
  const response = await apiFetch<{ data: { predictions: MistakePrediction[] } }>(`/v1/mistake-intelligence/mistakes/predictions${query}`);
  return response.data;
}

export async function getHighRiskConcepts(threshold = 0.7): Promise<{ high_risk_concepts: string[]; threshold: number }> {
  const query = buildQueryParams({ threshold });
  const response = await apiFetch<{ data: { high_risk_concepts: string[]; threshold: number } }>(`/v1/mistake-intelligence/mistakes/high-risk${query}`);
  return response.data;
}

export async function getImprovementTrend(concept: string): Promise<{ concept: string; trend: string }> {
  const response = await apiFetch<{ data: { concept: string; trend: string } }>(`/v1/mistake-intelligence/mistakes/trend/${concept}`);
  return response.data;
}

export async function clusterMistakes(minClusterSize = 2): Promise<{ clusters: MistakeCluster[]; stats: Record<string, unknown> }> {
  const query = buildQueryParams({ min_cluster_size: minClusterSize });
  const response = await apiFetch<{ data: { clusters: MistakeCluster[]; stats: Record<string, unknown> } }>(`/v1/mistake-intelligence/mistakes/cluster${query}`, {
    method: "POST",
  });
  return response.data;
}

export async function getIntelligenceReport(): Promise<IntelligenceReport> {
  const response = await apiFetch<{ data: IntelligenceReport }>("/v1/mistake-intelligence/mistakes/report");
  return response.data;
}
