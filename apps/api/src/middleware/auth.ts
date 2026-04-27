import type { MiddlewareHandler } from 'hono';
import { verifyAccessToken } from '../lib/jwt.js';
import type { Env } from '../lib/env.js';

export function bearerAuth(env: Env): MiddlewareHandler {
  return async (c, next) => {
    const auth = c.req.header('Authorization');
    if (!auth?.startsWith('Bearer ')) {
      return c.json({ error: 'Unauthorized' }, 401);
    }
    const token = auth.slice('Bearer '.length).trim();
    try {
      const userId = await verifyAccessToken(token, env);
      c.set('userId', userId);
      await next();
    } catch {
      return c.json({ error: 'Unauthorized' }, 401);
    }
  };
}
