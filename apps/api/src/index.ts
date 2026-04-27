import 'dotenv/config';

import { serve } from '@hono/node-server';
import { loadEnv } from './lib/env.js';
import { createApp } from './app.js';

const env = loadEnv();
const app = createApp(env);

const port = Number(process.env.PORT) || 3000;

serve({
  fetch: app.fetch,
  port,
});

console.log(`API listening on http://localhost:${port}`);
