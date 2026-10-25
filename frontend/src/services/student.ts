import { getStoredToken } from './auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface StudentProfileDetailed {
  id: string;
  user_id: string;
  roll_number: string;
  cgpa: number | null;
  placement_status: 'NOT_PLACED' | 'IN_PROCESS' | 'PLACED' | 'OPTED_OUT';
  user_full_name: string;
  user_email: string;
  institution_id: string;
  institution_name: string;
  department_id: string | null;
  department_name: string | null;
  department_code: string | null;
  cohort_id: string;
  cohort_graduation_year: number | null;
  cohort_section: string | null;
}

export interface StudentProfileUpdateRequest {
  full_name?: string;
  roll_number?: string;
  cgpa?: number;
  placement_status?: string;
}

export interface PreparationActivity {
  id: string;
  user_id: string;
  activity_type: string;
  category: string;
  topic: string;
  duration_minutes: number;
  completion_state: 'COMPLETED' | 'IN_PROGRESS' | 'ABANDONED';
  provenance: 'STUDENT_LOGGED' | 'SYSTEM_EVALUATED';
  notes: string | null;
  activity_date: string;
  created_at: string;
  updated_at: string;
}

export interface PreparationActivityListResponse {
  items: PreparationActivity[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PreparationActivityCreate {
  activity_type: string;
  category: string;
  topic: string;
  duration_minutes: number;
  completion_state?: string;
  notes?: string;
  activity_date?: string;
}

export interface LearningGoal {
  id: string;
  user_id: string;
  title: string;
  category: string;
  target_type: 'QUESTIONS_COUNT' | 'MINUTES_PRACTICED' | 'ACCURACY_PERCENT';
  target_value: number;
  current_value: number;
  deadline: string | null;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'ARCHIVED';
  progress_percentage: number;
  created_at: string;
  updated_at: string;
}

export interface LearningGoalCreate {
  title: string;
  category: string;
  target_type: string;
  target_value: number;
  deadline?: string;
}

export interface LearningGoalUpdate {
  title?: string;
  category?: string;
  target_type?: string;
  target_value?: number;
  current_value?: number;
  deadline?: string;
  status?: string;
}

export interface StudentWorkspaceSummary {
  total_activities: number;
  total_duration_minutes: number;
  completed_activities: number;
  unique_topics_count: number;
  active_goals_count: number;
  completed_goals_count: number;
  category_minutes: Record<string, number>;
  recent_activities: PreparationActivity[];
}

function getAuthHeaders(): HeadersInit {
  const token = getStoredToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function fetchStudentProfile(): Promise<StudentProfileDetailed> {
  const response = await fetch(`${API_BASE_URL}/student/profile`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch student profile');
  }
  return response.json();
}

export async function updateStudentProfile(payload: StudentProfileUpdateRequest): Promise<StudentProfileDetailed> {
  const response = await fetch(`${API_BASE_URL}/student/profile`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to update student profile');
  }
  return response.json();
}

export async function fetchWorkspaceSummary(): Promise<StudentWorkspaceSummary> {
  const response = await fetch(`${API_BASE_URL}/student/workspace-summary`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch workspace summary');
  }
  return response.json();
}

export async function fetchActivities(params?: {
  page?: number;
  page_size?: number;
  category?: string;
  activity_type?: string;
  completion_state?: string;
}): Promise<PreparationActivityListResponse> {
  const url = new URL(`${API_BASE_URL}/student/activities`);
  if (params?.page) url.searchParams.set('page', params.page.toString());
  if (params?.page_size) url.searchParams.set('page_size', params.page_size.toString());
  if (params?.category) url.searchParams.set('category', params.category);
  if (params?.activity_type) url.searchParams.set('activity_type', params.activity_type);
  if (params?.completion_state) url.searchParams.set('completion_state', params.completion_state);

  const response = await fetch(url.toString(), {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch preparation activities');
  }
  return response.json();
}

export async function createActivity(payload: PreparationActivityCreate): Promise<PreparationActivity> {
  const response = await fetch(`${API_BASE_URL}/student/activities`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to record preparation activity');
  }
  return response.json();
}

export async function deleteActivity(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/student/activities/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to delete preparation activity');
  }
}

export async function fetchGoals(status?: string): Promise<LearningGoal[]> {
  const url = new URL(`${API_BASE_URL}/student/goals`);
  if (status) url.searchParams.set('status', status);

  const response = await fetch(url.toString(), {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to fetch learning goals');
  }
  return response.json();
}

export async function createGoal(payload: LearningGoalCreate): Promise<LearningGoal> {
  const response = await fetch(`${API_BASE_URL}/student/goals`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to create learning goal');
  }
  return response.json();
}

export async function updateGoal(id: string, payload: LearningGoalUpdate): Promise<LearningGoal> {
  const response = await fetch(`${API_BASE_URL}/student/goals/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to update learning goal');
  }
  return response.json();
}

export async function deleteGoal(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/student/goals/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || 'Failed to delete learning goal');
  }
}
