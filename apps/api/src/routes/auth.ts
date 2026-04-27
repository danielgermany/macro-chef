import { Hono } from 'hono';
import { z } from 'zod';
import type { Env } from '../lib/env.js';
import { prisma } from '../lib/prisma.js';
import { hashPassword, verifyPassword } from '../lib/password.js';
import { signAccessToken } from '../lib/jwt.js';
import { bearerAuth } from '../middleware/auth.js';

const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  displayName: z.string().max(120).optional(),
});

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

function serializeUser(user: {
  id: string;
  email: string;
  displayName: string | null;
  createdAt: Date;
}) {
  return {
    id: user.id,
    email: user.email,
    displayName: user.displayName,
    createdAt: user.createdAt.toISOString(),
  };
}

export function createAuthRoutes(env: Env) {
  const r = new Hono<{ Variables: { userId: string } }>();

  r.post('/register', async (c) => {
    let body: unknown;
    try {
      body = await c.req.json();
    } catch {
      return c.json({ error: 'Invalid JSON' }, 400);
    }
    const parsed = registerSchema.safeParse(body);
    if (!parsed.success) {
      return c.json({ error: 'Validation failed', details: parsed.error.flatten() }, 400);
    }
    const { email, password, displayName } = parsed.data;

    const existing = await prisma.user.findUnique({ where: { email } });
    if (existing) {
      return c.json({ error: 'Email already registered' }, 409);
    }

    const passwordHash = await hashPassword(password);
    const user = await prisma.user.create({
      data: {
        email,
        passwordHash,
        displayName: displayName ?? null,
      },
    });

    const accessToken = await signAccessToken(user.id, env);

    return c.json(
      {
        accessToken,
        user: serializeUser(user),
      },
      201
    );
  });

  r.post('/login', async (c) => {
    let body: unknown;
    try {
      body = await c.req.json();
    } catch {
      return c.json({ error: 'Invalid JSON' }, 400);
    }
    const parsed = loginSchema.safeParse(body);
    if (!parsed.success) {
      return c.json({ error: 'Validation failed', details: parsed.error.flatten() }, 400);
    }
    const { email, password } = parsed.data;

    const user = await prisma.user.findUnique({ where: { email } });
    if (!user) {
      return c.json({ error: 'Invalid email or password' }, 401);
    }
    const ok = await verifyPassword(password, user.passwordHash);
    if (!ok) {
      return c.json({ error: 'Invalid email or password' }, 401);
    }

    const accessToken = await signAccessToken(user.id, env);

    return c.json({
      accessToken,
      user: serializeUser(user),
    });
  });

  r.post('/logout', async (c) => {
    return c.body(null, 204);
  });

  r.get('/me', bearerAuth(env), async (c) => {
    const userId = c.get('userId');
    const user = await prisma.user.findUnique({ where: { id: userId } });
    if (!user) {
      return c.json({ error: 'User not found' }, 404);
    }
    return c.json({ user: serializeUser(user) });
  });

  return r;
}
