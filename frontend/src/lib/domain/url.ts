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
export function sitePath(raw: string | null): string {
	if (!raw || !raw.startsWith('/')) return '/';
	// "//evil.test" and "/\evil.test" are protocol-relative addresses, not paths of this site.
	if (raw.startsWith('//') || raw.startsWith('/\\')) return '/';
	try {
		const url = new URL(raw, 'http://site.invalid');
		return `${url.pathname}${url.search}`;
	} catch {
		return '/';
	}
}
