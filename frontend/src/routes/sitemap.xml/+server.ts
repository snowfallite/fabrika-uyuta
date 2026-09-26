import { env } from '$env/dynamic/public';
import { buildSitemap } from '$lib/domain/sitemap';
import { createApi } from '$lib/server/api';
import { apiData } from '$lib/server/load';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ fetch }) => {
	const home = await apiData(createApi(fetch).GET('/api/v1/home/'));
	return new Response(buildSitemap(env.PUBLIC_SITE_URL ?? '', home.categories), {
		headers: { 'content-type': 'application/xml; charset=utf-8' }
	});
};
