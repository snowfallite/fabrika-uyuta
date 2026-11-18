import { expect, test, type Page } from '@playwright/test';
import { expectNoSeriousA11yViolations } from './axe';

const PAGES = ['/', '/catalog/kitchens', '/catalog/office', '/lead', '/privacy', '/consent'];

async function meta(page: Page, path: string) {
	await page.goto(path);
	const head = page.locator('head');
	const content = (selector: string) => head.locator(selector).first().getAttribute('content');
	return {
		title: await page.title(),
		description: await content('meta[name="description"]'),
		canonical: await head.locator('link[rel="canonical"]').getAttribute('href'),
		ogTitle: await content('meta[property="og:title"]'),
		ogDescription: await content('meta[property="og:description"]'),
		ogUrl: await content('meta[property="og:url"]'),
		robots: (await head.locator('meta[name="robots"]').count()) > 0
	};
}

test.describe('seo', () => {
	test('AC1: every page has a unique title and description, canonical and OG tags', async ({
		page,
		baseURL
	}) => {
		const origin = new URL(baseURL ?? 'http://localhost:8080').origin;
		const seen = { titles: new Set<string>(), descriptions: new Set<string>() };
		for (const path of PAGES) {
			const tags = await meta(page, path);
			expect(tags.title, path).toBeTruthy();
			expect(tags.description, path).toBeTruthy();
			expect(seen.titles.has(tags.title), `${path} title repeats`).toBe(false);
			expect(seen.descriptions.has(tags.description ?? ''), `${path} description repeats`).toBe(
				false
			);
			seen.titles.add(tags.title);
			seen.descriptions.add(tags.description ?? '');
			expect(tags.canonical).toBe(origin + path);
			expect(tags.ogUrl).toBe(origin + path);
			expect(tags.ogTitle).toBe(tags.title);
			expect(tags.ogDescription).toBe(tags.description);
			expect(tags.robots, path).toBe(path === '/lead');
		}
	});

	test('AC2: the sitemap lists static pages and published categories', async ({
		request,
		baseURL
	}) => {
		const origin = new URL(baseURL ?? 'http://localhost:8080').origin;
		const response = await request.get('/sitemap.xml');
		expect(response.headers()['content-type']).toContain('application/xml');
		const locs = [...(await response.text()).matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
		expect(locs).toEqual(
			[
				'/',
				'/privacy',
				'/consent',
				'/catalog/kitchens',
				'/catalog/kitchen-tables',
				'/catalog/wardrobes',
				'/catalog/sliding-wardrobes',
				'/catalog/office',
				'/catalog/other'
			].map((path) => origin + path)
		);
	});

	test('AC3: outside production robots.txt disallows everything', async ({ request }) => {
		expect(await (await request.get('/robots.txt')).text()).toBe('User-agent: *\nDisallow: /\n');
	});

	test('AC4: the home page carries FurnitureStore JSON-LD', async ({ page, baseURL }) => {
		const origin = new URL(baseURL ?? 'http://localhost:8080').origin;
		await page.goto('/');
		const raw = await page.locator('script[type="application/ld+json"]').textContent();
		const data = JSON.parse(raw ?? '{}');
		expect(data).toMatchObject({
			'@context': 'https://schema.org',
			'@type': 'FurnitureStore',
			name: 'Фабрика Уюта',
			url: `${origin}/`,
			telephone: '+78172000000',
			address: 'Вологда'
		});
		expect(data.image).toMatch(new RegExp(`^${origin}/media/content/`));
	});

	test('AC5: legal pages open from the footer and from the form', async ({ page }) => {
		await page.goto('/');
		await page.getByRole('contentinfo').getByRole('link', { name: 'Политика обработки' }).click();
		await expect(page).toHaveURL(/\/privacy$/);
		await expect(page.getByRole('heading', { level: 1 })).toHaveText(
			'Политика обработки персональных данных'
		);
		await page.goto('/');
		await page
			.getByRole('contentinfo')
			.getByRole('link', { name: 'Согласие на обработку' })
			.click();
		await expect(page).toHaveURL(/\/consent$/);
		await page.goto('/lead');
		await page.getByRole('link', { name: 'обработку персональных данных', exact: true }).click();
		await expect(page).toHaveURL(/\/consent$/);
		await expect(page.getByRole('heading', { level: 1 })).toHaveText(
			'Согласие на обработку персональных данных'
		);
	});

	test('favicon and manifest are served', async ({ request }) => {
		expect((await request.get('/favicon.svg')).ok()).toBe(true);
		const manifest = await (await request.get('/manifest.webmanifest')).json();
		expect(manifest.name).toBe('Фабрика Уюта');
	});

	for (const path of ['/privacy', '/consent']) {
		test(`axe finds no serious issues on ${path}`, async ({ page }) => {
			await page.goto(path, { waitUntil: 'networkidle' });
			await expectNoSeriousA11yViolations(page);
		});
	}
});
