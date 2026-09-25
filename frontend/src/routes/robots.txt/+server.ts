import { env } from '$env/dynamic/public';
import type { RequestHandler } from './$types';

/** Only production is indexable (tech.md, 10.1 and 16.1). */
export const GET: RequestHandler = () => {
	const body =
		env.PUBLIC_APP_ENV === 'production'
			? `User-agent: *\nAllow: /\n\nSitemap: ${env.PUBLIC_SITE_URL}/sitemap.xml\n`
			: 'User-agent: *\nDisallow: /\n';
	return new Response(body, { headers: { 'content-type': 'text/plain; charset=utf-8' } });
};
