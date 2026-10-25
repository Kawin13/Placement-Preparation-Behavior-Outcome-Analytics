import { getStoredToken } from './auth';

const API_BASE = '/api/v1';

export interface PreparationTimeBreakdown {
  total_hours: number;
  measured_platform_hours: number;
  self_logged_hours: number;
  measured_sessions_count: number;
  self_logged_activities_count: number;
  provenance_note: string;
}

export interface SkillGapItem {
  domain: string;
  domain_name: string;
  attempts_count: number;
  correct_count: number;
  accuracy_percentage: number | null;
  skill_gap_index: number | null;
  status: 'PROFICIENT' | 'MODERATE' | 'NEEDS_ATTENTION' | 'INSUFFICIENT_DATA';
  evidence_note: string;
}

export interface TopicPerformanceItem {
  topic_name: string;
  domain: string;
  attempts_count: number;
  correct_count: number;
  accuracy_percentage: number | null;
  difficulty_factor: number;
  status: 'PROFICIENT' | 'MODERATE' | 'NEEDS_ATTENTION' | 'INSUFFICIENT_DATA';
  evidence_note: string;
}

export interface DailyTrendPoint {
  date: string;
  active_minutes: number;
  measured_minutes: number;
  self_logged_minutes: number;
  attempts_count: number;
  accuracy_percentage: number | null;
}

export interface StudentAnalytics {
  student_id: string;
  student_name: string;
  roll_number: string | null;
  cohort_name: string | null;
  time_window: string;
  prep_time: PreparationTimeBreakdown;
  total_evaluated_attempts: number;
  overall_accuracy_percentage: number | null;
  mistake_remediation_rate: number | null;
  total_mistakes_logged: number;
  mastered_mistakes_count: number;
  skill_gaps: SkillGapItem[];
  topic_breakdown: TopicPerformanceItem[];
  daily_trends: DailyTrendPoint[];
  data_limitation_notice: string;
}

export interface CohortTopicFrictionPoint {
  topic_name: string;
  domain: string;
  cohort_attempts: number;
  cohort_accuracy_percentage: number;
  severity: 'HIGH_FRICTION' | 'MODERATE_FRICTION' | 'STABLE';
}

export interface PlacementCorrelationDiagnostic {
  sample_size: number;
  is_statistically_valid: boolean;
  spearman_rho: number | null;
  significance_note: string;
  non_causal_disclaimer: string;
}

export interface CohortAnalytics {
  cohort_id: string;
  cohort_name: string;
  department_name: string;
  graduation_year: number;
  section: string | null;
  total_enrolled_students: number;
  active_participating_students: number;
  participation_rate_percentage: number;
  total_cohort_active_hours: number;
  cohort_average_accuracy: number | null;
  skill_gap_distribution: Record<string, Record<string, number>>;
  topic_friction_points: CohortTopicFrictionPoint[];
  placement_correlation: PlacementCorrelationDiagnostic;
  data_freshness_timestamp: string;
}

function getAuthHeaders(): HeadersInit {
  const token = getStoredToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function fetchStudentAnalytics(
  days = 30,
  skillDomain?: string,
  studentId?: string
): Promise<StudentAnalytics> {
  const params = new URLSearchParams();
  if (days) params.append('days', days.toString());
  if (skillDomain) params.append('skill_domain', skillDomain);
  if (studentId) params.append('student_id', studentId);

  const res = await fetch(`${API_BASE}/analytics/student?${params.toString()}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch student analytics');
  }
  return res.json();
}

export async function fetchCohortAnalytics(
  cohortId?: string,
  departmentId?: string,
  days = 30
): Promise<CohortAnalytics> {
  const params = new URLSearchParams();
  if (cohortId) params.append('cohort_id', cohortId);
  if (departmentId) params.append('department_id', departmentId);
  if (days) params.append('days', days.toString());

  const res = await fetch(`${API_BASE}/analytics/cohort?${params.toString()}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch cohort analytics');
  }
  return res.json();
}

export async function downloadCohortReport(cohortId: string): Promise<void> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/analytics/export?cohort_id=${cohortId}`, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to download cohort report');
  }

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `cohort_telemetry_${cohortId}.csv`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}
