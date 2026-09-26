import { describe, expect, it, vi } from 'vitest';

const env = vi.hoisted(() => ({ PUBLIC_APP_ENV: 'dev', PUBLIC_SITE_URL: 'https://example.com' }));
vi.mock('$env/dynamic/public', () => ({ env }));

const { GET } = await import('./+server');
const robots = async () => (await GET({} as Parameters<typeof GET>[0])).text();

describe('/robots.txt', () => {
	it('AC3: production allows indexing and points to the sitemap', async () => {
		env.PUBLIC_APP_ENV = 'production';
		expect(await robots()).toBe(
			'User-agent: *\nAllow: /\n\nSitemap: https://example.com/sitemap.xml\n'
		);
	});

	it.each(['dev', 'e2e', 'staging'])('AC3: %s disallows everything', async (name) => {
		env.PUBLIC_APP_ENV = name;
		expect(await robots()).toBe('User-agent: *\nDisallow: /\n');
	});
});
