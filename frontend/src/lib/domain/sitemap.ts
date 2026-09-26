import type { CategorySummary } from '$lib/types';
import { absoluteUrl } from './url';

/** Indexable pages besides categories; /lead is noindex and stays out. */
const STATIC_PATHS = ['/', '/privacy', '/consent'];

const escapeXml = (value: string) =>
	value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

/** XML sitemap: static pages plus the published categories the API returned (tech.md, 10.4). */
export function buildSitemap(origin: string, categories: CategorySummary[]): string {
	const paths = new Set([...STATIC_PATHS, ...categories.map((c) => `/catalog/${c.slug}`)]);
	const urls = [...paths]
		.map((path) => `  <url><loc>${escapeXml(absoluteUrl(origin, path))}</loc></url>`)
		.join('\n');
	return (
		'<?xml version="1.0" encoding="UTF-8"?>\n' +
		'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
		`${urls}\n</urlset>\n`
	);
}
