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
});
