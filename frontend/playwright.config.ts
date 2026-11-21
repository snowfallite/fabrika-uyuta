import { defineConfig, devices } from '@playwright/test';

const baseURL = process.env.E2E_BASE_URL ?? 'http://localhost:8080';

const ACCEPTED_COOKIES = {
	cookies: [
		{
			name: 'cookie_consent',
			value: '1',
			domain: new URL(baseURL).hostname,
			path: '/',
			expires: -1,
			httpOnly: true,
			secure: false,
			sameSite: 'Lax' as const
		}
	],
	origins: []
};

export default defineConfig({
	testDir: 'tests/e2e',
	forbidOnly: !!process.env.CI,
	retries: process.env.CI ? 1 : 0,
	// A freshly started stack answers its first requests slowly.
	expect: { timeout: 10_000 },
	reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : 'list',
	use: {
		baseURL,
		// Every spec but cookies.spec.ts runs as a visitor who already pressed OK in the notice.
		storageState: ACCEPTED_COOKIES,
		// Reveal animations off: axe and screenshots see final colors.
		reducedMotion: 'reduce',
		trace: 'retain-on-failure'
	},
	projects: [
		{
			name: 'desktop',
			use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 900 } }
		},
		{
			name: 'mobile',
			use: { ...devices['Desktop Chrome'], viewport: { width: 360, height: 780 } }
		}
	]
});
