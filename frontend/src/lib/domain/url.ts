/** Absolute URL for canonical and Open Graph tags: origin plus a path, one slash between. */
export function absoluteUrl(origin: string, path: string): string {
	const base = origin.replace(/\/+$/, '');
	const tail = path.replace(/^\/+/, '').replace(/\/{2,}/g, '/');
	return `${base}/${tail}`;
}
