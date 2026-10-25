import { getStoredToken } from './auth';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface AssessmentListItem {
  id: string;
  institution_id: string;
  title: string;
  description: string | null;
  category: string | null;
  duration_minutes: number;
  passing_score: number | null;
  version: number;
  is_published: boolean;
  question_count: number;
  total_points: number;
  created_at: string;
}

export interface CandidateOption {
  id: string;
  option_text: string;
}

export interface CandidateQuestion {
  id: string;
  title: string;
  content: string;
  question_type: string;
  difficulty: string;
  points: number;
  order_index: number;
  options: CandidateOption[];
  saved_answer?: string | null;
}

export interface ActiveSession {
  session_id: string;
  assessment_id: string;
  assessment_title: string;
  assessment_category: string | null;
  session_type: string;
  status: string;
  duration_minutes: number;
  time_spent_seconds: number;
  started_at: string;
  questions: CandidateQuestion[];
}

export interface SubmitResult {
  session_id: string;
  status: string;
  total_score: number;
  max_score: number;
  percentage: number;
  is_passed: boolean | null;
  questions_count: number;
  correct_count: number;
  incorrect_count: number;
  unanswered_count: number;
  time_spent_seconds: number;
  completed_at: string;
}

export interface ReviewOption {
  id: string;
  option_text: string;
  is_correct: boolean;
  feedback: string | null;
}

export interface ReviewQuestion {
  id: string;
  title: string;
  content: string;
  question_type: string;
  difficulty: string;
  points: number;
  order_index: number;
  explanation: string | null;
  options: ReviewOption[];
  submitted_answer: string | null;
  is_correct: boolean;
  score_awarded: number;
  time_spent_ms: number;
}

export interface SessionReview {
  session_id: string;
  assessment_title: string;
  assessment_category: string | null;
  status: string;
  total_score: number;
  max_score: number;
  percentage: number;
  time_spent_seconds: number;
  started_at: string;
  completed_at: string | null;
  questions: ReviewQuestion[];
}

export interface MistakeEntry {
  id: string;
  question_id: string;
  question_title: string;
  question_content: string;
  question_type: string;
  skill_domain: string | null;
  student_notes: string | null;
  error_tag: string | null;
  mastery_status: 'UNRESOLVED' | 'REVIEWED' | 'MASTERED';
  created_at: string;
  resolved_at: string | null;
}

function getAuthHeaders(): HeadersInit {
  const token = getStoredToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function fetchAssessments(category?: string): Promise<AssessmentListItem[]> {
  const query = category ? `?category=${encodeURIComponent(category)}` : '';
  const res = await fetch(`${API_BASE}/practice/assessments${query}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch assessments');
  }
  return res.json();
}

export async function startPracticeSession(assessmentId: string, sessionType = 'PRACTICE'): Promise<ActiveSession> {
  const res = await fetch(`${API_BASE}/practice/sessions`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ assessment_id: assessmentId, session_type: sessionType }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to start session');
  }
  return res.json();
}

export async function fetchActiveSession(sessionId: string): Promise<ActiveSession> {
  const res = await fetch(`${API_BASE}/practice/sessions/${sessionId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch session state');
  }
  return res.json();
}

export async function saveSessionAnswer(
  sessionId: string,
  questionId: string,
  answer: string,
  timeSpentMs = 0
): Promise<void> {
  const res = await fetch(`${API_BASE}/practice/sessions/${sessionId}/save-answer`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      question_id: questionId,
      submitted_answer: answer,
      time_spent_ms: timeSpentMs,
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to save answer');
  }
}

export async function submitPracticeSession(
  sessionId: string,
  timeSpentSeconds?: number
): Promise<SubmitResult> {
  const query = timeSpentSeconds ? `?time_spent_seconds=${timeSpentSeconds}` : '';
  const res = await fetch(`${API_BASE}/practice/sessions/${sessionId}/submit${query}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to submit session');
  }
  return res.json();
}

export async function fetchSessionReview(sessionId: string): Promise<SessionReview> {
  const res = await fetch(`${API_BASE}/practice/sessions/${sessionId}/review`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch session review');
  }
  return res.json();
}

export async function fetchStudentMistakes(masteryStatus?: string): Promise<MistakeEntry[]> {
  const query = masteryStatus ? `?mastery_status=${encodeURIComponent(masteryStatus)}` : '';
  const res = await fetch(`${API_BASE}/practice/mistakes${query}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch mistakes');
  }
  return res.json();
}

export async function updateMistakeEntry(
  mistakeId: string,
  data: { mastery_status: string; student_notes?: string; error_tag?: string }
): Promise<void> {
  const res = await fetch(`${API_BASE}/practice/mistakes/${mistakeId}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to update mistake');
  }
}
