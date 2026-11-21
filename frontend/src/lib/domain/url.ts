/** Absolute URL for canonical and Open Graph tags: origin plus a path, one slash between. */
export function absoluteUrl(origin: string, path: string): string {
	const base = origin.replace(/\/+$/, '');
	const tail = path.replace(/^\/+/, '').replace(/\/{2,}/g, '/');
	return `${base}/${tail}`;
}

/**
 * Keeps only this site's own path: "/catalog/kitchens?a=b" survives, a foreign or
 * malformed address becomes "/" (tech.md, 10.4). Guards the redirect of /cookie-consent.
 */
const SITE_BASE = 'http://site.invalid';

export function sitePath(raw: string | null): string {
	if (!raw || !raw.startsWith('/')) return '/';
	try {
		const url = new URL(raw, SITE_BASE);
		// "//evil.test/x" and "/\evil.test/x" carry a host of their own: they leave this site.
		if (url.origin !== SITE_BASE) return '/';
		const path = `${url.pathname}${url.search}`;
		// "/..//evil.test" keeps our origin but normalizes into a protocol-relative address.
		return path.startsWith('//') || path.startsWith('/\\') ? '/' : path;
	} catch {
		return '/';
	}
}
