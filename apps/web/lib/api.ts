const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
const STATIC_TOKEN = process.env.NEXT_PUBLIC_API_TOKEN ?? '';
let runtimeToken = STATIC_TOKEN;

if (typeof window !== 'undefined') {
  const stored = window.localStorage.getItem('crdc-precheck-token');
  if (stored) {
    runtimeToken = stored;
  }
}

type District = {
  id: string;
  name: string;
  timezone: string;
};

type RuleRun = {
  id: string;
  status: string;
  created_at: string;
  finished_at: string | null;
};

type RuleResult = {
  id: string;
  message: string;
  severity: string;
  status: string;
  created_at: string;
};

export type StudentCsvMapping = {
  sis_id: string;
  first_name: string;
  last_name: string;
  grade_level: string;
  school_name: string;
  enrollment_status?: string;
  ell_status?: string;
  idea_flag?: string;
};

export type CsvImportResponse = {
  rows_processed: number;
  students_created: number;
  students_updated: number;
  errors: string[];
  ingest_batch_id: string;
};

export type ExceptionRecord = {
  id: string;
  district_id: string;
  rule_result_id: string;
  owner_user_id: string | null;
  status: string;
  rationale: string | null;
  due_date: string | null;
  approval_user_id: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ReadinessItem = {
  school_id: string | null;
  school_name: string | null;
  category: string;
  score: number;
  open_errors: number;
  open_warnings: number;
};

export type ReadinessResponse = {
  items: ReadinessItem[];
};

export type AuthResponse = {
  token: string;
  user: {
    id: string;
    district_id: string;
    email: string;
    display_name: string;
    role: string;
  };
};

export function setAuthToken(token: string) {
  runtimeToken = token;
  if (typeof window !== 'undefined') {
    window.localStorage.setItem('crdc-precheck-token', token);
  }
}

export function getAuthToken(): string {
  return runtimeToken;
}

type RequestHeaders = HeadersInit | undefined;

function buildHeaders(extra?: RequestHeaders): HeadersInit {
  const base: Record<string, string> = { 'Content-Type': 'application/json' };
  const token = getAuthToken();
  if (token) {
    base.Authorization = `Bearer ${token}`;
  }

  if (!extra) {
    return base;
  }

  if (extra instanceof Headers) {
    const merged = new Headers(extra);
    Object.entries(base).forEach(([key, value]) => {
      if (!merged.has(key)) {
        merged.set(key, value);
      }
    });
    return merged;
  }

  return { ...base, ...(extra as Record<string, string>) };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: buildHeaders(init?.headers),
    cache: 'no-store',
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }

  return (await response.json()) as T;
}

export async function fetchDistricts(): Promise<District[]> {
  return request<District[]>('/districts');
}

export async function fetchRuleRuns(districtId: string): Promise<RuleRun[]> {
  return request<RuleRun[]>(`/rules/runs`, {
    headers: { 'X-District-ID': districtId },
  });
}

export async function fetchRuleResults(
  districtId: string,
  ruleRunId?: string,
): Promise<RuleResult[]> {
  const search = ruleRunId ? `?rule_run_id=${ruleRunId}` : '';
  return request<RuleResult[]>(`/rules/results${search}`, {
    headers: { 'X-District-ID': districtId },
  });
}

export async function triggerRuleRun(districtId: string): Promise<RuleRun> {
  return request<RuleRun>('/rules/runs', {
    method: 'POST',
    headers: { 'X-District-ID': districtId },
    body: JSON.stringify({}),
  });
}

export async function triggerPowerschoolSync(districtId: string): Promise<{ status: string; task_id: string | null }> {
  return request<{ status: string; task_id: string | null }>('/connectors/powerschool/sync', {
    method: 'POST',
    headers: { 'X-District-ID': districtId },
  });
}

export async function uploadStudentCsv(
  districtId: string,
  file: File,
  mapping: StudentCsvMapping,
): Promise<CsvImportResponse> {
  const form = new FormData();
  form.append('file', file);
  form.append('mapping', JSON.stringify(mapping));

  const headers: Record<string, string> = { 'X-District-ID': districtId };
  const token = getAuthToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}/import/students/csv`, {
    method: 'POST',
    body: form,
    headers,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }

  return (await response.json()) as CsvImportResponse;
}

export async function fetchExceptions(districtId: string): Promise<ExceptionRecord[]> {
  return request<ExceptionRecord[]>('/exceptions', {
    headers: { 'X-District-ID': districtId },
  });
}

export async function updateException(
  districtId: string,
  exceptionId: string,
  data: Partial<{ status: string; owner_user_id: string; rationale: string; due_date: string; approved: boolean }>,
): Promise<ExceptionRecord> {
  return request<ExceptionRecord>(`/exceptions/${exceptionId}`, {
    method: 'PATCH',
    headers: { 'X-District-ID': districtId },
    body: JSON.stringify(data),
  });
}

export async function createEvidencePacket(
  districtId: string,
  payload: { name: string; description?: string | null; exception_ids: string[] },
): Promise<{ id: string }> {
  return request<{ id: string }>('/evidence/packets', {
    method: 'POST',
    headers: { 'X-District-ID': districtId },
    body: JSON.stringify(payload),
  });
}

export async function fetchReadiness(districtId: string): Promise<ReadinessResponse> {
  return request<ReadinessResponse>('/readiness', {
    headers: { 'X-District-ID': districtId },
  });
}

export async function loginSSO(
  districtId: string,
  payload: { provider: string; subject: string; email: string; display_name: string },
): Promise<AuthResponse> {
  const response = await request<AuthResponse>('/auth/sso', {
    method: 'POST',
    headers: { 'X-District-ID': districtId },
    body: JSON.stringify(payload),
  });
  setAuthToken(response.token);
  return response;
}

export async function fetchAdminHealth(districtId: string): Promise<any> {
  return request('/admin/health', {
    headers: { 'X-District-ID': districtId },
  });
}

export async function downloadExceptionsCsv(districtId: string): Promise<Blob> {
  const headers = buildHeaders({ 'X-District-ID': districtId });
  const response = await fetch(`${API_BASE}/exports/exceptions.csv`, {
    method: 'GET',
    headers,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return await response.blob();
}
