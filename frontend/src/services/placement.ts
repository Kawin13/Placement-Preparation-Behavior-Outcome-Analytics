import { getStoredToken } from './auth';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export type PlacementTier =
  | 'TIER_1_PRODUCT'
  | 'TIER_2_FINTECH'
  | 'TIER_3_CONSULTING_IT'
  | 'STARTUP';

export type VerificationStatus =
  | 'PENDING_REVIEW'
  | 'OFFICIALLY_VERIFIED'
  | 'REJECTED'
  | 'WITHDRAWN';

export interface PlacementOutcomeRecord {
  id: string;
  user_id: string;
  student_name?: string;
  student_roll_number?: string;
  company_name: string;
  job_title: string;
  tier: PlacementTier;
  ctc_lpa: number | null;
  offer_date: string | null;
  proof_document_url: string | null;
  verification_status: VerificationStatus;
  verified_by_user_id: string | null;
  rejection_reason: string | null;
  verified_at: string | null;
  created_at: string;
}

export interface PlacementOutcomeCreatePayload {
  company_name: string;
  job_title: string;
  tier: PlacementTier;
  ctc_lpa?: number | null;
  offer_date?: string | null;
  proof_document_url?: string | null;
  target_user_id?: string | null; // Officers only
}

export interface PlacementOutcomeUpdatePayload {
  company_name?: string;
  job_title?: string;
  tier?: PlacementTier;
  ctc_lpa?: number | null;
  offer_date?: string | null;
  proof_document_url?: string | null;
}

export interface PlacementOutcomeVerifyPayload {
  verification_status: 'OFFICIALLY_VERIFIED' | 'REJECTED' | 'PENDING_REVIEW';
  rejection_reason?: string;
}

export interface PlacementBatchImportItem {
  roll_number: string;
  company_name: string;
  job_title: string;
  tier: PlacementTier;
  ctc_lpa?: number | null;
  offer_date?: string | null;
  auto_verify?: boolean;
}

export interface PlacementBatchImportResponse {
  total_processed: number;
  created_count: number;
  duplicate_count: number;
  error_count: number;
  errors: string[];
  created_ids: string[];
}

export async function fetchPlacementOutcomes(filters?: {
  status_filter?: string;
  tier_filter?: string;
  user_id?: string;
  limit?: number;
  offset?: number;
}): Promise<PlacementOutcomeRecord[]> {
  const token = getStoredToken();
  const params = new URLSearchParams();
  if (filters?.status_filter) params.set('status_filter', filters.status_filter);
  if (filters?.tier_filter) params.set('tier_filter', filters.tier_filter);
  if (filters?.user_id) params.set('user_id', filters.user_id);
  if (filters?.limit) params.set('limit', filters.limit.toString());
  if (filters?.offset) params.set('offset', filters.offset.toString());

  const res = await fetch(`${API_BASE}/placement/outcomes?${params.toString()}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Failed to fetch placement outcomes');
  }

  return res.json();
}

export async function submitPlacementOutcome(
  payload: PlacementOutcomeCreatePayload
): Promise<PlacementOutcomeRecord> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/placement/outcomes`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Failed to submit placement outcome');
  }

  return res.json();
}

export async function updatePlacementOutcome(
  outcomeId: string,
  payload: PlacementOutcomeUpdatePayload
): Promise<PlacementOutcomeRecord> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/placement/outcomes/${outcomeId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Failed to update placement outcome');
  }

  return res.json();
}

export async function verifyPlacementOutcome(
  outcomeId: string,
  payload: PlacementOutcomeVerifyPayload
): Promise<PlacementOutcomeRecord> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/placement/outcomes/${outcomeId}/verify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Failed to verify placement outcome');
  }

  return res.json();
}

export async function withdrawPlacementOutcome(
  outcomeId: string
): Promise<PlacementOutcomeRecord> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/placement/outcomes/${outcomeId}/withdraw`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Failed to withdraw placement outcome');
  }

  return res.json();
}

export async function exportPlacementOutcomesCsv(): Promise<string> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/placement/export/csv`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Failed to export placement report');
  }

  return res.text();
}

export async function batchImportPlacementOutcomes(
  items: PlacementBatchImportItem[]
): Promise<PlacementBatchImportResponse> {
  const token = getStoredToken();
  const res = await fetch(`${API_BASE}/placement/batch-import`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ items }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || 'Failed to batch import placement outcomes');
  }

  return res.json();
}
