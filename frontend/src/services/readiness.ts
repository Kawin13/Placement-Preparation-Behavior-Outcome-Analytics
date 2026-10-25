import { getStoredToken } from './auth';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface DomainWeightRequirement {
  domain: string;
  domain_name: string;
  weight: number;
  min_attempts: number;
  target_accuracy: number;
}

export interface RoleDefinition {
  role_id: string;
  role_name: string;
  description: string;
  target_industry_tier: string;
  domain_requirements: DomainWeightRequirement[];
}

export interface DomainEvidenceItem {
  domain: string;
  domain_name: string;
  weight: number;
  attempts_count: number;
  correct_count: number;
  raw_accuracy_percentage: number | null;
  weighted_domain_score: number | null;
  meets_threshold: boolean;
  attempts_needed: number;
  recency_days_ago: number | null;
  recency_label: string;
  status: 'PROFICIENT' | 'MODERATE' | 'NEEDS_ATTENTION' | 'INSUFFICIENT_EVIDENCE';
  evidence_note: string;
}

export interface PracticeRecommendation {
  assessment_id: string;
  assessment_title: string;
  domain: string;
  category: string;
  duration_minutes: number;
  priority: 'CRITICAL_DEFICIT' | 'HIGH_PRIORITY' | 'REINFORCEMENT';
  rationale: string;
}

export interface RoleReadinessResponse {
  student_id: string;
  student_name: string;
  roll_number: string | null;
  role_id: string;
  role_name: string;
  role_description: string;
  target_industry_tier: string;
  readiness_score: number | null; // Suppressed if insufficient evidence
  readiness_tier: 'ROLE_READY' | 'DEVELOPING' | 'FOUNDATION_NEEDED' | 'INSUFFICIENT_EVIDENCE';
  has_sufficient_evidence: boolean;
  total_role_attempts: number;
  domain_evidence: DomainEvidenceItem[];
  missing_evidence_summary: string[];
  recommendations: PracticeRecommendation[];
  non_predictive_disclaimer: string;
  formula_documentation: string;
  last_evaluated_at: string;
}

export async function fetchApprovedRoles(): Promise<RoleDefinition[]> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/readiness/roles`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch approved roles');
  }

  return res.json();
}

export async function evaluateRoleReadiness(
  roleId: string,
  studentId?: string
): Promise<RoleReadinessResponse> {
  const token = getStoredToken();
  const params = new URLSearchParams({ role_id: roleId });
  if (studentId) {
    params.set('student_id', studentId);
  }

  const res = await fetch(`${API_BASE}/readiness/evaluate?${params.toString()}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to evaluate role readiness');
  }

  return res.json();
}
