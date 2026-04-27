import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { loadEnv } from './lib/env.js';
import { prisma } from './lib/prisma.js';
import { createApp } from './app.js';

const enabled =
  Boolean(process.env.DATABASE_URL) &&
  Boolean(process.env.JWT_SECRET && process.env.JWT_SECRET.length >= 32);

describe.skipIf(!enabled)('meal tenant isolation', () => {
  const suffix = Math.random().toString(36).slice(2);
  const emailA = `user_a_${suffix}@test.example`;
  const emailB = `user_b_${suffix}@test.example`;

  let app: ReturnType<typeof createApp>;
  let tokenA = '';
  let tokenB = '';

  beforeAll(async () => {
    await prisma.mealLog.deleteMany({});
    await prisma.user.deleteMany({
      where: { email: { in: [emailA, emailB] } },
    });

    const env = loadEnv();
    app = createApp(env);
  });

  afterAll(async () => {
    await prisma.mealLog.deleteMany({});
    await prisma.user.deleteMany({
      where: { email: { in: [emailA, emailB] } },
    });
    await prisma.$disconnect();
  });

  it('registers two users and obtains tokens', async () => {
    const ra = await app.request('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: emailA,
        password: 'password1x',
        displayName: 'User A',
      }),
    });
    expect(ra.status).toBe(201);
    const ja = (await ra.json()) as { accessToken: string };
    tokenA = ja.accessToken;

    const rb = await app.request('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: emailB,
        password: 'password1y',
      }),
    });
    expect(rb.status).toBe(201);
    const jb = (await rb.json()) as { accessToken: string };
    tokenB = jb.accessToken;
  });

  it('user A logs a meal; user B does not see it on the same date', async () => {
    const today = new Date().toISOString().slice(0, 10);

    const post = await app.request('/api/meals', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${tokenA}`,
      },
      body: JSON.stringify({
        name: 'Oatmeal',
        calories: 300,
      }),
    });
    expect(post.status).toBe(201);

    const listA = await app.request(`/api/meals?date=${today}`, {
      headers: { Authorization: `Bearer ${tokenA}` },
    });
    expect(listA.status).toBe(200);
    const dataA = (await listA.json()) as { meals: { name: string }[] };
    expect(dataA.meals.some((m) => m.name === 'Oatmeal')).toBe(true);

    const listB = await app.request(`/api/meals?date=${today}`, {
      headers: { Authorization: `Bearer ${tokenB}` },
    });
    expect(listB.status).toBe(200);
    const dataB = (await listB.json()) as { meals: { name: string }[] };
    expect(dataB.meals.some((m) => m.name === 'Oatmeal')).toBe(false);
  });
});
