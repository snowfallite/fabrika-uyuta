import { describe, expect, it } from 'vitest';
import fc from 'fast-check';
import type { CategorySlug, CategorySummary } from '$lib/types';
import { buildSitemap } from './sitemap';

const numRuns = process.env.CI ? 200 : 50;
const SLUGS: CategorySlug[] = [
	'kitchens',
	'kitchen-tables',
	'wardrobes',
	'sliding-wardrobes',
	'office'
];
const ORIGIN = 'https://example.com';

const category = (slug: CategorySlug): CategorySummary => ({
	slug,
	title: slug,
	short_description: '',
	cover: null,
	updated_at: '2026-11-20T10:00:00Z'
});

const locs = (xml: string) => [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1] ?? '');

describe('buildSitemap', () => {
	it('lists static pages and the given categories', () => {
		expect(locs(buildSitemap(ORIGIN, [category('office')]))).toEqual([
			'https://example.com/',
			'https://example.com/privacy',
			'https://example.com/consent',
			'https://example.com/cookies',
			'https://example.com/catalog/office'
		]);
	});

	it('AC2: exactly the published categories, no duplicates, absolute URLs', () => {
		fc.assert(
			fc.property(
				fc.array(fc.constantFrom(...SLUGS)),
				fc.constantFrom(ORIGIN, `${ORIGIN}/`, 'http://localhost:8080'),
				(published, origin) => {
					const urls = locs(buildSitemap(origin, published.map(category)));
					const base = origin.replace(/\/$/, '');
					expect(new Set(urls).size).toBe(urls.length);
					for (const url of urls) expect(url.startsWith(`${base}/`)).toBe(true);
					for (const slug of SLUGS) {
						const listed = urls.includes(`${base}/catalog/${slug}`);
						expect(listed).toBe(published.includes(slug));
					}
					expect(urls).toContain(`${base}/`);
					expect(urls).not.toContain(`${base}/lead`);
				}
			),
			{ numRuns }
		);
	});

	it('AC6: a category carries its edit time, static pages carry none', () => {
		const xml = buildSitemap(ORIGIN, [
			{ ...category('office'), updated_at: '2026-11-18T08:30:00Z' }
		]);

		expect(xml).toContain(
			'<url><loc>https://example.com/catalog/office</loc><lastmod>2026-11-18T08:30:00Z</lastmod></url>'
		);
		expect(xml).toContain('<url><loc>https://example.com/</loc></url>');
	});

	it('AC6: every category gets exactly one lastmod', () => {
		fc.assert(
			fc.property(fc.array(fc.constantFrom(...SLUGS), { maxLength: 5 }), (published) => {
				const dated = published.map((slug, index) => ({
					...category(slug),
					updated_at: `2026-11-1${index}T10:00:00Z`
				}));
				const entries = [...buildSitemap(ORIGIN, dated).matchAll(/ {2}<url>(.*)<\/url>/g)].map(
					(match) => match[1] ?? ''
				);

				for (const entry of entries) {
					expect(entry.includes('<lastmod>')).toBe(entry.includes('/catalog/'));
				}
				expect(entries.filter((entry) => entry.includes('<lastmod>')).length).toBe(
					new Set(published).size
				);
			}),
			{ numRuns }
		);
	});
});
