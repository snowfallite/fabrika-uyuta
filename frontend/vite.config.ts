import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vitest/config';
import { loadEnv } from 'vite';
import { playwright } from '@vitest/browser-playwright';
import { sveltekit } from '@sveltejs/kit/vite';

// One .env at the repository root serves backend and frontend (tech.md, section 14).
const envDir = '..';

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, envDir, '');
	const backend = 'http://localhost:8000';

	return {
		envDir,
		plugins: [tailwindcss(), sveltekit()],
		server: {
			// Caddy routes these to Django in containers (tech.md, 16.4).
			proxy: {
				'/media': backend,
				'/django-static': backend,
				[`/${env.DJANGO_ADMIN_PATH || 'admin/'}`]: backend
			}
		},
		test: {
			expect: { requireAssertions: true },
			projects: [
				{
					extends: './vite.config.ts',
					test: {
						name: 'client',
						browser: {
							enabled: true,
							provider: playwright(),
							instances: [{ browser: 'chromium', headless: true }]
						},
						include: ['src/**/*.svelte.{test,spec}.{js,ts}'],
						exclude: ['src/lib/server/**']
					}
				},
				{
					extends: './vite.config.ts',
					test: {
						name: 'server',
						environment: 'node',
						include: ['src/**/*.{test,spec}.{js,ts}'],
						exclude: ['src/**/*.svelte.{test,spec}.{js,ts}']
					}
				}
			]
		}
	};
});
