import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    setupFiles: ['./vitest.setup.ts'],
    environment: 'node',
    include: ['src/**/*.integration.test.ts'],
    poolOptions: {
      threads: { singleThread: true },
    },
    sequence: {
      concurrent: false,
    },
  },
});
