import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['tests/unit/**/*.test.ts'],
    environment: 'node',
    // JUnit is the lingua franca here: unit, API and UI tests all emit it, so one
    // mechanism reports all three. Today every test type reports differently, which
    // is the most common reason nobody looks at the results.
    reporters: process.env.CI ? ['default', 'junit'] : ['default'],
    outputFile: { junit: 'reports/unit.xml' },
  },
});
