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
		ogImage: await content('meta[property="og:image"]'),
		twitterCard: await content('meta[name="twitter:card"]'),
		twitterTitle: await content('meta[name="twitter:title"]'),
		twitterDescription: await content('meta[name="twitter:description"]'),
		twitterImage: await content('meta[name="twitter:image"]'),
		robots: (await head.locator('meta[name="robots"]').count()) > 0
	};
}

/** Every JSON-LD block of the page, parsed; the home page carries two of them. */
async function jsonLd(page: Page): Promise<Record<string, unknown>[]> {
	const blocks = await page.locator('script[type="application/ld+json"]').allTextContents();
	return blocks.map((raw) => JSON.parse(raw) as Record<string, unknown>);
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

	test('S2-18 AC2: every page shares with a picture and a twitter card', async ({
		page,
		baseURL
	}) => {
		test.slow(); // One pass over every page: the default timeout is too tight for six loads.
		const origin = new URL(baseURL ?? 'http://localhost:8080').origin;
		for (const path of PAGES) {
			const tags = await meta(page, path);
			expect(tags.ogImage, path).toMatch(new RegExp(`^${origin}/`));
			expect(tags.twitterCard, path).toBe('summary_large_image');
			expect(tags.twitterTitle, path).toBe(tags.title);
			expect(tags.twitterDescription, path).toBe(tags.description);
			expect(tags.twitterImage, path).toBe(tags.ogImage);
		}
	});

	test('S2-18 AC2: a page without a photo of its own shows the site cover', async ({
		page,
		request,
		baseURL
	}) => {
		const origin = new URL(baseURL ?? 'http://localhost:8080').origin;

		expect((await meta(page, '/privacy')).ogImage).toBe(`${origin}/og-cover.png`);
		expect((await meta(page, '/catalog/kitchens')).ogImage).toMatch(
			new RegExp(`^${origin}/media/content/`)
		);
		expect((await request.get('/og-cover.png')).ok()).toBe(true);
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

	test('S2-18 AC6: categories carry lastmod, static pages carry none', async ({ request }) => {
		const xml = await (await request.get('/sitemap.xml')).text();
		const entries = [
			...xml.matchAll(/<url><loc>([^<]+)<\/loc>(?:<lastmod>([^<]+)<\/lastmod>)?<\/url>/g)
		];

		expect(entries).toHaveLength(9);
		for (const [, loc, lastmod] of entries) {
			if (loc?.includes('/catalog/')) {
				expect(lastmod, loc).toBeTruthy();
				expect(Number.isNaN(Date.parse(lastmod ?? '')), loc).toBe(false);
			} else {
				expect(lastmod, loc).toBeUndefined();
			}
		}
	});

	test('AC3: outside production robots.txt disallows everything', async ({ request }) => {
		expect(await (await request.get('/robots.txt')).text()).toBe('User-agent: *\nDisallow: /\n');
	});

	test('AC4: the home page carries FurnitureStore JSON-LD', async ({ page, baseURL }) => {
		const origin = new URL(baseURL ?? 'http://localhost:8080').origin;
		await page.goto('/');
		const [store] = await jsonLd(page);
		expect(store).toMatchObject({
			'@context': 'https://schema.org',
			'@type': 'FurnitureStore',
			name: 'Фабрика Уюта',
			url: `${origin}/`,
			telephone: '+78172000000',
			email: 'info@example.ru',
			address: {
				'@type': 'PostalAddress',
				addressLocality: 'Вологда',
				streetAddress: 'ул. Мира, 1'
			},
			sameAs: ['https://vk.com/']
		});
		expect(store?.image).toMatch(new RegExp(`^${origin}/media/content/`));
	});

	test('S2-18 AC5: the home page lists its categories in order', async ({ page, baseURL }) => {
		const origin = new URL(baseURL ?? 'http://localhost:8080').origin;
		await page.goto('/');

		const list = (await jsonLd(page)).find((block) => block['@type'] === 'ItemList');
		const items = (list?.itemListElement ?? []) as Record<string, unknown>[];

		expect(items).toHaveLength(6);
		expect(items.slice(0, 2)).toMatchObject([
			{ position: 1, name: 'Кухни под заказ', url: `${origin}/catalog/kitchens` },
			{ position: 2, name: 'Кухонные столы', url: `${origin}/catalog/kitchen-tables` }
		]);
		expect(items.at(-1)).toMatchObject({
			position: 6,
			name: 'Другое',
			url: `${origin}/catalog/other`
		});
	});

	test('S2-18 AC4: the category page shows its path and marks it up', async ({ page, baseURL }) => {
		const origin = new URL(baseURL ?? 'http://localhost:8080').origin;
		await page.goto('/catalog/kitchens');

		const crumbs = page.getByRole('navigation', { name: 'Хлебные крошки' });
		await expect(crumbs.getByRole('link', { name: 'Главная' })).toHaveAttribute('href', '/');
		await expect(crumbs.getByRole('link', { name: 'Направления' })).toHaveAttribute(
			'href',
			'/#catalog'
		);
		await expect(crumbs.getByText('Кухни под заказ')).toBeVisible();

		const [path] = await jsonLd(page);
		expect(path).toMatchObject({
			'@type': 'BreadcrumbList',
			itemListElement: [
				{ position: 1, name: 'Главная', item: `${origin}/` },
				{ position: 2, name: 'Направления', item: `${origin}/#catalog` },
				{ position: 3, name: 'Кухни под заказ' }
			]
		});
		expect(
			Object.keys((path?.itemListElement as Record<string, unknown>[])[2] ?? {})
		).not.toContain('item');
	});

	test('S2-18 AC9: the markup parses and the policy blocks nothing', async ({ page }) => {
		const blocked: string[] = [];
		page.on('console', (message) => {
			if (message.type() === 'error' && /Content Security Policy/i.test(message.text())) {
				blocked.push(message.text());
			}
		});

		await page.goto('/', { waitUntil: 'networkidle' });
		expect((await jsonLd(page)).map((block) => block['@type'])).toEqual([
			'FurnitureStore',
			'ItemList'
		]);

		await page.goto('/catalog/kitchens', { waitUntil: 'networkidle' });
		expect((await jsonLd(page)).map((block) => block['@type'])).toEqual(['BreadcrumbList']);

		expect(blocked).toEqual([]);
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
