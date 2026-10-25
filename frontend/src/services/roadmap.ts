import { getStoredToken } from './auth';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

function getAuthHeaders(): HeadersInit {
  const token = getStoredToken();
  return {
    'Content-Type': 'application/json',
    Authorization: token ? `Bearer ${token}` : '',
  };
}

export interface CareerPathItem {
  id: string;
  code: string;
  title: string;
  description?: string | null;
  target_role: string;
  display_order: number;
}

export interface StudentCareerGoal {
  career_path_id: string;
  career_path_title: string;
  target_role: string;
  target_company_tier?: string | null;
  current_progress_pct: number;
  total_topics: number;
  completed_topics: number;
  created_at: string;
}

export interface RoadmapTopicSummary {
  id: string;
  slug: string;
  name: string;
  difficulty: string;
  estimated_minutes: number;
  display_order: number;
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED' | 'MASTERED';
  accuracy_rate: number;
  questions_attempted: number;
  resources_count: number;
  dsa_problems_count: number;
}

export interface RoadmapSubjectTree {
  id: string;
  code: string;
  name: string;
  description?: string | null;
  icon: string;
  display_order: number;
  topics: RoadmapTopicSummary[];
  progress_pct: number;
}

export interface RoadmapTree {
  career_path: CareerPathItem;
  overall_progress_pct: number;
  subjects: RoadmapSubjectTree[];
  total_topics: number;
  completed_topics: number;
}

export interface LearningResourceSummary {
  id: string;
  title: string;
  resource_type: string;
  estimated_minutes: number;
  difficulty: string;
  external_url?: string | null;
  is_completed: boolean;
}

export interface LearningResourceDetail extends LearningResourceSummary {
  description?: string | null;
  content?: string | null;
}

export interface TopicPracticeQuestion {
  id: string;
  title: string;
  content: string;
  difficulty: string;
  points: number;
  attempts_count: number;
  user_accuracy?: number | null;
  is_solved?: boolean;
}

export interface TopicDSAProblem {
  id: string;
  problem_number: number;
  slug: string;
  title: string;
  difficulty: string;
  status: 'UNSOLVED' | 'ATTEMPTED' | 'SOLVED';
}

export interface TopicDetail {
  id: string;
  subject_name: string;
  slug: string;
  name: string;
  description?: string | null;
  learning_objectives?: string | null;
  difficulty: string;
  estimated_minutes: number;
  status: string;
  accuracy_rate: number;
  questions_attempted: number;
  coding_problems_solved: number;
  evidence_confidence: 'INSUFFICIENT' | 'LOW' | 'MODERATE' | 'HIGH';
  resources: LearningResourceSummary[];
  practice_questions: TopicPracticeQuestion[];
  dsa_problems: TopicDSAProblem[];
  recommended_next_step: string;
}

export interface NextActionResponse {
  action_type: 'SELECT_PATH' | 'STUDY_RESOURCE' | 'PRACTICE_QUESTIONS' | 'SOLVE_DSA' | 'REVISE_MISTAKES';
  title: string;
  reason: string;
  target_id?: string | null;
  target_slug?: string | null;
  path_url?: string | null;
}

export async function fetchCareerPaths(): Promise<CareerPathItem[]> {
  const res = await fetch(`${API_BASE}/roadmap/career-paths`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch career paths');
  return res.json();
}

export async function selectCareerPath(careerPathId: string, tier?: string): Promise<StudentCareerGoal> {
  const res = await fetch(`${API_BASE}/roadmap/select-path`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ career_path_id: careerPathId, target_company_tier: tier }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || err.detail || 'Failed to select career path');
  }
  return res.json();
}

export async function fetchMyCareerGoal(): Promise<StudentCareerGoal | null> {
  const res = await fetch(`${API_BASE}/roadmap/my-goal`, {
    headers: getAuthHeaders(),
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error('Failed to fetch career goal');
  return res.json();
}

export async function fetchRoadmapTree(): Promise<RoadmapTree> {
  const res = await fetch(`${API_BASE}/roadmap/tree`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || err.detail || 'Failed to fetch roadmap tree');
  }
  return res.json();
}

export async function fetchTopicDetail(topicId: string): Promise<TopicDetail> {
  const res = await fetch(`${API_BASE}/roadmap/topics/${topicId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || err.detail || 'Failed to fetch topic detail');
  }
  return res.json();
}

export async function fetchResourceDetail(resourceId: string): Promise<LearningResourceDetail> {
  const res = await fetch(`${API_BASE}/roadmap/resources/${resourceId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch learning resource');
  return res.json();
}

export async function completeResource(resourceId: string, durationSeconds: number = 60): Promise<void> {
  const res = await fetch(`${API_BASE}/roadmap/resources/${resourceId}/complete?duration_seconds=${durationSeconds}`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to complete resource');
}

export async function fetchNextRecommendedAction(): Promise<NextActionResponse> {
  const res = await fetch(`${API_BASE}/roadmap/next-recommended-action`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch recommended action');
  return res.json();
}

export async function trackStudentBehaviorEvent(eventType: string, payload: {
  topic_id?: string;
  resource_id?: string;
  metadata?: Record<string, any>;
}): Promise<void> {
  try {
    await fetch(`${API_BASE}/roadmap/track-event`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        event_type: eventType,
        topic_id: payload.topic_id,
        resource_id: payload.resource_id,
        metadata_json: payload.metadata,
      }),
    });
  } catch {
    // Non-blocking telemetry
  }
}
