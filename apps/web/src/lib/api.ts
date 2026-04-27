const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:3000';

function authHeaders(): HeadersInit {
  const token = localStorage.getItem('access_token');
  const h: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) {
    h.Authorization = `Bearer ${token}`;
  }
  return h;
}

export async function apiRegister(body: {
  email: string;
  password: string;
  displayName?: string;
}): Promise<{ accessToken: string }> {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error((data as { error?: string }).error ?? `Register failed (${res.status})`);
  }
  return data as { accessToken: string };
}

export async function apiLogin(body: {
  email: string;
  password: string;
}): Promise<{ accessToken: string }> {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error((data as { error?: string }).error ?? `Login failed (${res.status})`);
  }
  return data as { accessToken: string };
}

export async function apiMe(): Promise<{
  user: { id: string; email: string; displayName: string | null; createdAt: string };
}> {
  const res = await fetch(`${API_BASE}/api/auth/me`, { headers: authHeaders() });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error((data as { error?: string }).error ?? `Session invalid (${res.status})`);
  }
  return data as {
    user: { id: string; email: string; displayName: string | null; createdAt: string };
  };
}

export async function apiCreateMeal(body: {
  name: string;
  eatenAt?: string;
  calories?: number;
  proteinG?: number;
  carbsG?: number;
  fatG?: number;
}): Promise<void> {
  const res = await fetch(`${API_BASE}/api/meals`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error((data as { error?: string }).error ?? `Save meal failed (${res.status})`);
  }
}

export async function apiListMeals(date: string): Promise<{
  date: string;
  meals: {
    id: string;
    name: string;
    eatenAt: string;
    mealDate: string;
    calories: number | null;
    proteinG: number | null;
    carbsG: number | null;
    fatG: number | null;
  }[];
}> {
  const res = await fetch(`${API_BASE}/api/meals?date=${encodeURIComponent(date)}`, {
    headers: authHeaders(),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error((data as { error?: string }).error ?? `Load meals failed (${res.status})`);
  }
  return data as {
    date: string;
    meals: {
      id: string;
      name: string;
      eatenAt: string;
      mealDate: string;
      calories: number | null;
      proteinG: number | null;
      carbsG: number | null;
      fatG: number | null;
    }[];
  };
}
