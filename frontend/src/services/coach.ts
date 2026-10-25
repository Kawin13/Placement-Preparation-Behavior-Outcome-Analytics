import { getStoredToken } from './auth';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface MistakeExplanationRequest {
  question_id: string;
  selected_answer?: string | null;
  student_notes?: string | null;
  error_tag?: string | null;
}

export interface MistakeExplanationResponse {
  question_id: string;
  question_title: string;
  concept_summary: string;
  detailed_proof_or_explanation: string;
  why_answer_was_incorrect: string | null;
  remedial_takeaway: string;
  recommended_topic: string;
  provider_used: 'GEMINI_EXTERNAL' | 'OFFLINE_GROUNDED_MENTOR' | string;
  is_grounded_in_syllabus: boolean;
  privacy_notice: string;
}

export interface StudyPlanItem {
  day_number: number;
  domain: string;
  topic_focus: string;
  action_type: 'PRACTICE_DRILL' | 'MISTAKE_REVIEW' | 'CONCEPT_STUDY';
  suggested_duration_minutes: number;
  suggested_assessment_id: string | null;
  suggested_assessment_title: string | null;
  pedagogical_objective: string;
}

export interface StudyPlanRequest {
  target_role_id?: string;
  weekly_hours_available?: number;
}

export interface StudyPlanResponse {
  student_id: string;
  target_role_id: string;
  target_role_name: string;
  plan_overview: string;
  schedule: StudyPlanItem[];
  provider_used: string;
  evidence_grounding_note: string;
  privacy_notice: string;
}

export async function explainMistake(
  req: MistakeExplanationRequest
): Promise<MistakeExplanationResponse> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/coach/explain-mistake`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to explain mistake');
  }

  return res.json();
}

export async function generateStudyPlan(
  req: StudyPlanRequest
): Promise<StudyPlanResponse> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/coach/generate-plan`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to generate study plan');
  }

  return res.json();
}
