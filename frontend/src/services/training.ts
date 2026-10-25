import { getStoredToken } from './auth';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface TrainingProgramItem {
  id: string;
  institution_id: string;
  title: string;
  description: string | null;
  domain: string;
  start_date: string;
  end_date: string;
  total_planned_hours: number;
  trainer_id: string | null;
  trainer_name: string | null;
  session_count: number;
  created_at: string;
}

export interface TrainingProgramCreatePayload {
  title: string;
  description?: string | null;
  domain: string;
  start_date: string;
  end_date: string;
  total_planned_hours: number;
  trainer_id?: string | null;
}

export interface TrainingSessionItem {
  id: string;
  program_id: string;
  session_date: string;
  start_time: string | null;
  duration_minutes: number;
  topic_covered: string;
  trainer_notes: string | null;
  created_at: string;
}

export interface TrainingSessionCreatePayload {
  program_id: string;
  session_date: string;
  start_time?: string | null;
  duration_minutes: number;
  topic_covered: string;
  trainer_notes?: string | null;
}

export interface AttendanceRecordItem {
  id: string;
  session_id: string;
  user_id: string;
  student_name?: string;
  roll_number?: string;
  attendance_status: 'PRESENT' | 'ABSENT' | 'EXCUSED';
  marked_by_user_id: string | null;
  marked_at: string;
}

export interface TrainingEffectivenessReport {
  program_id: string;
  program_title: string;
  domain: string;
  pre_window_start: string;
  pre_window_end: string;
  post_window_start: string;
  post_window_end: string;
  total_enrolled_count: number;
  matched_pairs_count: number;
  attrition_missing_count: number;
  mean_pre_score: number | null;
  mean_post_score: number | null;
  mean_score_delta: number | null;
  insufficient_data_reasons: string[];
  non_causal_disclaimer: string;
  methodology_notes: string;
  evaluated_at: string;
}

export async function fetchTrainingPrograms(domain?: string): Promise<TrainingProgramItem[]> {
  const token = getStoredToken();
  const url = domain
    ? `${API_BASE}/training/programs?domain=${encodeURIComponent(domain)}`
    : `${API_BASE}/training/programs`;

  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Failed to fetch training programs');
  }

  return res.json();
}

export async function fetchTrainingProgramDetail(programId: string): Promise<TrainingProgramItem> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/training/programs/${programId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Failed to fetch program detail');
  }

  return res.json();
}

export async function createTrainingProgram(
  payload: TrainingProgramCreatePayload
): Promise<TrainingProgramItem> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/training/programs`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Failed to create training program');
  }

  return res.json();
}

export async function fetchProgramSessions(programId: string): Promise<TrainingSessionItem[]> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/training/programs/${programId}/sessions`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Failed to fetch program sessions');
  }

  return res.json();
}

export async function createTrainingSession(
  payload: TrainingSessionCreatePayload
): Promise<TrainingSessionItem> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/training/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Failed to create training session');
  }

  return res.json();
}

export async function fetchSessionAttendance(sessionId: string): Promise<AttendanceRecordItem[]> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/training/sessions/${sessionId}/attendance`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Failed to fetch attendance records');
  }

  return res.json();
}

export async function recordSessionAttendance(
  sessionId: string,
  records: { user_id: string; attendance_status: 'PRESENT' | 'ABSENT' | 'EXCUSED' }[]
): Promise<AttendanceRecordItem[]> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/training/sessions/${sessionId}/attendance`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      session_id: sessionId,
      records,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Failed to record attendance');
  }

  return res.json();
}

export async function fetchProgramEffectiveness(
  programId: string
): Promise<TrainingEffectivenessReport> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/training/programs/${programId}/effectiveness`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Failed to fetch effectiveness report');
  }

  return res.json();
}
