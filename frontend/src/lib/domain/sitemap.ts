import type { CategorySummary } from '$lib/types';
import { absoluteUrl } from './url';

/** Indexable pages besides categories; /lead is noindex and stays out. */
const STATIC_PATHS = ['/', '/privacy', '/consent', '/cookies'];

const escapeXml = (value: string) =>
	value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

/** Static pages have no edit time of their own, so only categories carry lastmod (tech.md, v16). */
const entry = (loc: string, lastmod?: string) =>
	`  <url><loc>${escapeXml(loc)}</loc>` +
	(lastmod ? `<lastmod>${escapeXml(lastmod)}</lastmod>` : '') +
	'</url>';

/** XML sitemap: static pages plus the published categories the API returned (tech.md, 10.4). */
export function buildSitemap(origin: string, categories: CategorySummary[]): string {
	const seen = new Set(STATIC_PATHS);
	const urls = STATIC_PATHS.map((path) => entry(absoluteUrl(origin, path)));
	for (const category of categories) {
		const path = `/catalog/${category.slug}`;
		if (seen.has(path)) continue;
		seen.add(path);
		urls.push(entry(absoluteUrl(origin, path), category.updated_at));
	}
	return (
		'<?xml version="1.0" encoding="UTF-8"?>\n' +
		'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
		`${urls.join('\n')}\n</urlset>\n`
	);
}
