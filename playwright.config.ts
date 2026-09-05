import { defineConfig, devices } from '@playwright/test';

/**
 * Address of the application under test.
 *
 * By default we test an instance started locally (or on the CI runner). Setting `BASE_URL`
 * points the whole suite at any other environment - and that single variable is the only
 * difference between "testing on the runner" and "testing a deployed environment".
 */
const baseURL = process.env.BASE_URL ?? 'http://localhost:3000';

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: true,

  // A public-repository runner has four cores. The scaffolded default of one worker on CI
  // is copied into thousands of projects and almost never revisited - it was the single
  // cheapest optimisation in this whole pipeline, and it costs nothing in minutes.
  workers: process.env.CI ? 4 : undefined,

  // Retries buy time to diagnose without blocking the team. They do not fix anything:
  // the worst case gets three times longer and the problem is hidden rather than solved.
  // Playwright reports a test that passed on retry as "flaky", separately from "passed" -
  // that is a signal, not a success.
  retries: process.env.CI ? 2 : 0,

  // `blob` is an intermediate format built to be merged. Two HTML reports cannot be
  // combined in any meaningful way, which is why sharding quietly breaks reporting
  // unless this is changed alongside it.
  reporter: process.env.CI
    ? [['blob'], ['github']]
    : [['list'], ['html', { open: 'never' }]],

  use: {
    baseURL,
    // Trace everything, always. Convenient, but artifacts balloon - EXERCISE 15.
    trace: 'on',
    screenshot: 'only-on-failure',
  },

  // The server starts only when no external environment is given.
  // The build is no longer here: the application is built once, in its own job, and
  // arrives as an artifact. A compilation error now fails the build job, where it belongs,
  // instead of masquerading as a broken test.
  webServer: process.env.BASE_URL
    ? undefined
    : {
        command: 'npm start',
        url: 'http://localhost:3000/api/health',
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
      },

  projects: [
    {
      name: 'api',
      testDir: './tests/api',
      use: { baseURL },
    },
    {
      name: 'ui-chromium',
      testDir: './tests/ui',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
