import { Hono } from 'hono';
import { cors } from 'hono/cors';
import type { Env } from './lib/env.js';
import { createAuthRoutes } from './routes/auth.js';
import { createMealsRoutes } from './routes/meals.js';

export function createApp(env: Env) {
  const app = new Hono();

  app.use(
    '*',
    cors({
      origin: ['http://localhost:5173', 'http://127.0.0.1:5173'],
      allowHeaders: ['Authorization', 'Content-Type'],
      credentials: true,
    })
  );

  app.get('/', (c) =>
    c.json({ message: 'Macro Chef API', docs: 'OpenAPI TBD', health: '/health' })
  );

  app.get('/health', (c) =>
    c.json({ status: 'healthy', service: '@macro-chef/api' })
  );

  const api = new Hono();
  api.route('/auth', createAuthRoutes(env));
  api.route('/meals', createMealsRoutes(env));

  app.route('/api', api);

  return app;
}
