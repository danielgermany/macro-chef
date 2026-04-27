import { serve } from '@hono/node-server';
import { Hono } from 'hono';

const app = new Hono();

app.get('/', (c) =>
  c.json({ message: 'Macro Chef API', docs: 'OpenAPI TBD', health: '/health' })
);

app.get('/health', (c) =>
  c.json({ status: 'healthy', service: '@macro-chef/api' })
);

const port = Number(process.env.PORT) || 3000;

serve({
  fetch: app.fetch,
  port,
});

console.log(`API listening on http://localhost:${port}`);
