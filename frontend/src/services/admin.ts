import { getStoredToken, type UserSummary } from './auth';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface DomainAccuracyItem {
  domain: string;
  domain_name: string;
  total_attempts: number;
  correct_attempts: number;
  accuracy_percentage: number | null;
}

export interface ActivityCategoryItem {
  category: string;
  category_name: string;
  hours_spent: number;
  activity_count: number;
}

export interface TierDistributionItem {
  tier: string;
  tier_label: string;
  count: number;
  mean_ctc: number | null;
}

export interface EngagementPillar {
  total_enrolled_students: number;
  active_students_count: number;
  total_preparation_hours: number;
  total_activities_count: number;
  goal_completion_rate: number | null;
  activity_breakdown: ActivityCategoryItem[];
}

export interface AssessmentPillar {
  total_evaluations: number;
  overall_accuracy_percentage: number | null;
  domain_breakdown: DomainAccuracyItem[];
}

export interface TrainingPillar {
  total_programs_count: number;
  total_sessions_delivered: number;
  total_attendance_records: number;
  overall_attendance_rate: number | null;
  mean_paired_score_delta: number | null;
}

export interface PlacementPillar {
  total_reported_offers: number;
  verified_offers_count: number;
  pending_review_count: number;
  rejected_count: number;
  verified_placed_students_count: number;
  verified_placement_rate: number | null;
  mean_verified_ctc_lpa: number | null;
  max_verified_ctc_lpa: number | null;
  tier_distribution: TierDistributionItem[];
}

export interface CollegeIntelligenceOverview {
  institution_id: string;
  institution_name: string;
  generated_at: string;
  is_suppressed: boolean;
  suppression_reason: string | null;
  cohort_sample_size: number;
  department_filter: string | null;
  cohort_filter: string | null;
  date_window_start: string | null;
  date_window_end: string | null;
  engagement: EngagementPillar | null;
  assessments: AssessmentPillar | null;
  training: TrainingPillar | null;
  placement: PlacementPillar | null;
  non_causal_notice: string;
  audit_traceability_notice: string;
}

export interface DepartmentItem {
  id: string;
  institution_id: string;
  name: string;
  code: string;
}

export interface CohortItem {
  id: string;
  department_id: string;
  graduation_year: number;
  section: string | null;
  department?: DepartmentItem;
}

export interface AuditLogItem {
  id: string;
  institution_id: string;
  actor_user_id: string | null;
  action: string;
  entity_type: string;
  entity_id: string | null;
  ip_address: string | null;
  details_json: any;
  created_at: string;
}

export interface ContentBankSummary {
  total_assessments: number;
  published_assessments: number;
  total_questions: number;
  domains: {
    domain: string;
    question_count: number;
    assessment_count: number;
    total_attempts: number;
  }[];
}

export async function fetchCollegeIntelligenceOverview(filters?: {
  department_id?: string;
  cohort_id?: string;
  start_date?: string;
  end_date?: string;
}): Promise<CollegeIntelligenceOverview> {
  const token = getStoredToken();
  const params = new URLSearchParams();
  if (filters?.department_id) params.set('department_id', filters.department_id);
  if (filters?.cohort_id) params.set('cohort_id', filters.cohort_id);
  if (filters?.start_date) params.set('start_date', filters.start_date);
  if (filters?.end_date) params.set('end_date', filters.end_date);

  const res = await fetch(`${API_BASE}/admin/intelligence/overview?${params.toString()}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch college intelligence overview');
  }

  return res.json();
}

export async function exportCollegeIntelligenceCsv(filters?: {
  department_id?: string;
  cohort_id?: string;
}): Promise<string> {
  const token = getStoredToken();
  const params = new URLSearchParams();
  if (filters?.department_id) params.set('department_id', filters.department_id);
  if (filters?.cohort_id) params.set('cohort_id', filters.cohort_id);

  const res = await fetch(`${API_BASE}/admin/intelligence/export/csv?${params.toString()}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to export intelligence report');
  }

  return res.text();
}

export async function fetchAdminUsers(filters?: {
  role?: string;
  is_active?: boolean;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<UserSummary[]> {
  const token = getStoredToken();
  const params = new URLSearchParams();
  if (filters?.role) params.set('role', filters.role);
  if (filters?.is_active !== undefined) params.set('is_active', filters.is_active.toString());
  if (filters?.search) params.set('search', filters.search);
  if (filters?.limit) params.set('limit', filters.limit.toString());
  if (filters?.offset) params.set('offset', filters.offset.toString());

  const res = await fetch(`${API_BASE}/admin/users?${params.toString()}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch institutional users');
  }

  return res.json();
}

export async function updateUserStatus(userId: string, isActive: boolean): Promise<UserSummary> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/admin/users/${userId}/status`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ is_active: isActive }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to update user status');
  }

  return res.json();
}

export async function updateUserRole(userId: string, role: string): Promise<UserSummary> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/admin/users/${userId}/role`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ role }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to update user role');
  }

  return res.json();
}

export async function createStaffUser(payload: {
  email: string;
  password: string;
  full_name: string;
  role: string;
}): Promise<UserSummary> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/admin/users`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to provision staff account');
  }

  return res.json();
}

export async function fetchAdminDepartments(): Promise<DepartmentItem[]> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/admin/departments`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch departments');
  }

  return res.json();
}

export async function createDepartment(payload: { name: string; code: string }): Promise<DepartmentItem> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/admin/departments`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to create department');
  }

  return res.json();
}

export async function fetchAdminCohorts(): Promise<CohortItem[]> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/admin/cohorts`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch cohorts');
  }

  return res.json();
}

export async function createCohort(payload: {
  department_id: string;
  graduation_year: number;
  section?: string | null;
}): Promise<CohortItem> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/admin/cohorts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to create cohort');
  }

  return res.json();
}

export async function fetchAuditLogs(filters?: {
  action?: string;
  entity_type?: string;
  limit?: number;
  offset?: number;
}): Promise<AuditLogItem[]> {
  const token = getStoredToken();
  const params = new URLSearchParams();
  if (filters?.action) params.set('action', filters.action);
  if (filters?.entity_type) params.set('entity_type', filters.entity_type);
  if (filters?.limit) params.set('limit', filters.limit.toString());
  if (filters?.offset) params.set('offset', filters.offset.toString());

  const res = await fetch(`${API_BASE}/admin/audit-logs?${params.toString()}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch audit logs');
  }

  return res.json();
}

export async function exportAuditLogsCsv(): Promise<string> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/admin/audit-logs/export/csv`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to export audit trail');
  }

  return res.text();
}

export async function fetchContentBankSummary(): Promise<ContentBankSummary> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/admin/content/summary`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch content summary');
  }

  return res.json();
}
