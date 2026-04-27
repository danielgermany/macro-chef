import { Hono } from 'hono';
import { z } from 'zod';
import type { Env } from '../lib/env.js';
import { prisma } from '../lib/prisma.js';
import { bearerAuth } from '../middleware/auth.js';
import { parseUtcDateKey, toUtcMealDate, utcDateKey } from '../lib/meal-date.js';

const createMealSchema = z.object({
  name: z.string().min(1).max(200),
  eatenAt: z.string().datetime().optional(),
  calories: z.number().int().nonnegative().optional(),
  proteinG: z.number().nonnegative().optional(),
  carbsG: z.number().nonnegative().optional(),
  fatG: z.number().nonnegative().optional(),
});

function serializeMeal(row: {
  id: string;
  userId: string;
  eatenAt: Date;
  mealDate: Date;
  name: string;
  calories: number | null;
  proteinG: number | null;
  carbsG: number | null;
  fatG: number | null;
}) {
  return {
    id: row.id,
    userId: row.userId,
    eatenAt: row.eatenAt.toISOString(),
    mealDate: row.mealDate.toISOString().slice(0, 10),
    name: row.name,
    calories: row.calories,
    proteinG: row.proteinG,
    carbsG: row.carbsG,
    fatG: row.fatG,
  };
}

export function createMealsRoutes(env: Env) {
  const r = new Hono<{ Variables: { userId: string } }>();

  r.use('/*', bearerAuth(env));

  r.post('/', async (c) => {
    const userId = c.get('userId');
    let body: unknown;
    try {
      body = await c.req.json();
    } catch {
      return c.json({ error: 'Invalid JSON' }, 400);
    }
    const parsed = createMealSchema.safeParse(body);
    if (!parsed.success) {
      return c.json({ error: 'Validation failed', details: parsed.error.flatten() }, 400);
    }
    const { name, eatenAt, calories, proteinG, carbsG, fatG } = parsed.data;

    const eaten = eatenAt ? new Date(eatenAt) : new Date();
    const mealDate = toUtcMealDate(eaten);

    const meal = await prisma.mealLog.create({
      data: {
        userId,
        eatenAt: eaten,
        mealDate,
        name,
        calories: calories ?? null,
        proteinG: proteinG ?? null,
        carbsG: carbsG ?? null,
        fatG: fatG ?? null,
      },
    });

    return c.json({ meal: serializeMeal(meal) }, 201);
  });

  r.get('/', async (c) => {
    const userId = c.get('userId');
    const dateParam = c.req.query('date');
    const dateKey =
      dateParam && /^\d{4}-\d{2}-\d{2}$/.test(dateParam)
        ? dateParam
        : utcDateKey(new Date());

    let dayStart: Date;
    try {
      dayStart = parseUtcDateKey(dateKey);
    } catch {
      return c.json({ error: 'Invalid date query (use YYYY-MM-DD)' }, 400);
    }

    const meals = await prisma.mealLog.findMany({
      where: {
        userId,
        mealDate: dayStart,
      },
      orderBy: { eatenAt: 'desc' },
    });

    return c.json({
      date: dateKey,
      meals: meals.map(serializeMeal),
    });
  });

  r.delete('/:id', async (c) => {
    const userId = c.get('userId');
    const id = c.req.param('id');
    const result = await prisma.mealLog.deleteMany({
      where: { id, userId },
    });
    if (result.count === 0) {
      return c.json({ error: 'Not found' }, 404);
    }
    return c.body(null, 204);
  });

  return r;
}
