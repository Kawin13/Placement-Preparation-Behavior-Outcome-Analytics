import { getStoredToken } from './auth';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface DSATopicItem {
  id: string;
  slug: string;
  name: string;
  order_index: number;
  summary: string | null;
  problem_count: number;
  solved_count: number;
}

export interface DSAProblemListItem {
  id: string;
  problem_number: number;
  slug: string;
  title: string;
  difficulty: 'EASY' | 'MEDIUM' | 'HARD';
  topic_name: string | null;
  topic_slug: string | null;
  sheet_tags: string[];
  is_problem_of_the_day: boolean;
  status: string;
  user_status: 'UNSOLVED' | 'ATTEMPTED' | 'SOLVED';
  acceptance_rate: number;
}

export interface ExampleCase {
  input: string;
  output: string;
  explanation?: string | null;
}

export interface VisibleTestCase {
  case_index: number;
  input_data: string;
  expected_output: string;
}

export interface DSAProblemDetail {
  id: string;
  problem_number: number;
  slug: string;
  title: string;
  difficulty: 'EASY' | 'MEDIUM' | 'HARD';
  topic_id: string | null;
  topic_name: string | null;
  topic_slug: string | null;
  description: string;
  constraints: string | null;
  input_format: string | null;
  output_format: string | null;
  examples: ExampleCase[];
  starter_code: Record<string, string>;
  expected_time_complexity: string | null;
  expected_space_complexity: string | null;
  hints: string[];
  sample_test_cases: VisibleTestCase[];
  sheet_tags: string[];
  is_problem_of_the_day: boolean;
  user_status: 'UNSOLVED' | 'ATTEMPTED' | 'SOLVED';
}

export interface DSARunCaseResult {
  case_index: number;
  input_data: string;
  expected_output?: string | null;
  actual_output?: string | null;
  passed: boolean;
  execution_time_ms: number;
  error?: string | null;
}

export interface DSARunCodeResponse {
  status: string;
  results: DSARunCaseResult[];
  custom_result?: DSARunCaseResult | null;
  stdout?: string | null;
  compilation_error?: string | null;
}

export interface DSASubmitResponse {
  submission_id: string;
  verdict: 'ACCEPTED' | 'WRONG_ANSWER' | 'COMPILATION_ERROR' | 'RUNTIME_ERROR' | 'TIME_LIMIT_EXCEEDED';
  runtime_ms: number | null;
  memory_kb: number | null;
  test_cases_passed: number;
  total_test_cases: number;
  failed_test_case_index: number | null;
  error_message: string | null;
  is_first_solve: boolean;
  accuracy_percentage: number;
}

export interface DSASubmissionHistoryItem {
  id: string;
  submitted_at: string;
  language: string;
  verdict: string;
  runtime_ms: number | null;
  memory_kb: number | null;
  test_cases_passed: number;
  total_test_cases: number;
}

export interface DSAEditorialResponse {
  problem_id: string;
  problem_number: number;
  title: string;
  editorial: string | null;
  expected_time_complexity: string | null;
  expected_space_complexity: string | null;
  reference_solutions: Record<string, string>;
}

export interface DSATopicStat {
  topic_name: string;
  topic_slug: string;
  total_problems: number;
  solved_problems: number;
  accuracy_percentage: number;
}

export interface DSAStudentAnalyticsResponse {
  total_solved: number;
  easy_solved: number;
  medium_solved: number;
  hard_solved: number;
  total_problems: number;
  total_submissions: number;
  acceptance_rate: number;
  topic_stats: DSATopicStat[];
  recommended_problem_slug: string | null;
  recommended_problem_title: string | null;
  recommended_reason: string | null;
}

function getAuthHeaders(): HeadersInit {
  const token = getStoredToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function fetchDSATopics(): Promise<DSATopicItem[]> {
  const res = await fetch(`${API_BASE}/dsa/topics`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || err.detail || 'Failed to fetch DSA topics');
  }
  return res.json();
}

export async function fetchDSAProblems(params?: {
  topic_slug?: string;
  difficulty?: string;
  status?: string;
  sheet_tag?: string;
  search?: string;
}): Promise<DSAProblemListItem[]> {
  const query = new URLSearchParams();
  if (params?.topic_slug) query.set('topic_slug', params.topic_slug);
  if (params?.difficulty) query.set('difficulty', params.difficulty);
  if (params?.status) query.set('status', params.status);
  if (params?.sheet_tag) query.set('sheet_tag', params.sheet_tag);
  if (params?.search) query.set('search', params.search);

  const qs = query.toString() ? `?${query.toString()}` : '';
  const res = await fetch(`${API_BASE}/dsa/problems${qs}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || err.detail || 'Failed to fetch DSA problems');
  }
  return res.json();
}

export async function fetchProblemOfTheDay(): Promise<DSAProblemListItem> {
  const res = await fetch(`${API_BASE}/dsa/problems/potd`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || err.detail || 'Failed to fetch Problem of the Day');
  }
  return res.json();
}

export async function fetchProblemDetails(slug: string): Promise<DSAProblemDetail> {
  const res = await fetch(`${API_BASE}/dsa/problems/${encodeURIComponent(slug)}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || err.detail || 'Failed to fetch problem details');
  }
  return res.json();
}

export async function runDSACode(
  slug: string,
  payload: { language: string; code: string; custom_input?: string }
): Promise<DSARunCodeResponse> {
  const res = await fetch(`${API_BASE}/dsa/problems/${encodeURIComponent(slug)}/run`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || err.detail || 'Code execution failed');
  }
  return res.json();
}

export async function submitDSASolution(
  slug: string,
  payload: { language: string; code: string; hints_viewed?: number }
): Promise<DSASubmitResponse> {
  const res = await fetch(`${API_BASE}/dsa/problems/${encodeURIComponent(slug)}/submit`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || err.detail || 'Solution submission failed');
  }
  return res.json();
}

export async function fetchSubmissionHistory(slug: string): Promise<DSASubmissionHistoryItem[]> {
  const res = await fetch(`${API_BASE}/dsa/problems/${encodeURIComponent(slug)}/submissions`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || err.detail || 'Failed to fetch submission history');
  }
  return res.json();
}

export async function fetchProblemEditorial(slug: string): Promise<DSAEditorialResponse> {
  const res = await fetch(`${API_BASE}/dsa/problems/${encodeURIComponent(slug)}/editorial`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || err.detail || 'Failed to fetch editorial');
  }
  return res.json();
}

export async function fetchMyDSAAnalytics(): Promise<DSAStudentAnalyticsResponse> {
  const res = await fetch(`${API_BASE}/dsa/analytics/me`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || err.detail || 'Failed to fetch DSA analytics');
  }
  return res.json();
}
