const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface UserSummary {
  id: string;
  email: string;
  full_name: string;
  role: string;
  institution_id: string;
  is_active?: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserSummary;
}

export interface InstitutionItem {
  id: string;
  name: string;
  code: string;
  is_active: boolean;
}

// Token management in localStorage
export function getStoredToken(): string | null {
  return localStorage.getItem('access_token');
}

export function setStoredToken(token: string): void {
  localStorage.setItem('access_token', token);
}

export function removeStoredToken(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_info');
}

export function getStoredUser(): UserSummary | null {
  const raw = localStorage.getItem('user_info');
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setStoredUser(user: UserSummary): void {
  localStorage.setItem('user_info', JSON.stringify(user));
}

// API Calls
export async function loginUser(email: string, password: string): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Login failed. Please check your credentials.');
  }

  setStoredToken(data.access_token);
  setStoredUser(data.user);
  return data;
}

export async function registerStudent(payload: {
  email: string;
  password: string;
  full_name: string;
  institution_id: string;
  roll_number?: string;
}): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || 'Registration failed.');
  }

  setStoredToken(data.access_token);
  setStoredUser(data.user);
  return data;
}

export async function fetchInstitutions(): Promise<InstitutionItem[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/institutions/`);
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export async function requestPasswordReset(email: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });
  return response.json();
}
