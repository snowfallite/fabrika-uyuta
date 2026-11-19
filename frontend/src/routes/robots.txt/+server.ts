import { env } from '$env/dynamic/public';
import type { RequestHandler } from './$types';

// Yandex folds /lead?product=<slug> into one address: the preselected kind shows the same page.
// Disallow would hide the page instead, and the robot would never read its noindex (tech.md, v16).
const CLEAN_PARAM = 'Clean-param: product /lead';

/** Only production is indexable (tech.md, 10.1 and 16.1). */
export const GET: RequestHandler = () => {
	const body =
		env.PUBLIC_APP_ENV === 'production'
			? `User-agent: *\nAllow: /\n${CLEAN_PARAM}\n\nSitemap: ${env.PUBLIC_SITE_URL}/sitemap.xml\n`
			: 'User-agent: *\nDisallow: /\n';
	return new Response(body, { headers: { 'content-type': 'text/plain; charset=utf-8' } });
};
