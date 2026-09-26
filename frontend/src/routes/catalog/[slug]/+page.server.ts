import { createApi } from '$lib/server/api';
import { apiData } from '$lib/server/load';
import type { PageServerLoad } from './$types';

// Unknown or hidden categories come back as API 404 and render the 404 page.
export const load: PageServerLoad = async ({ fetch, params }) => ({
	category: await apiData(
		createApi(fetch).GET('/api/v1/categories/{slug}/', { params: { path: { slug: params.slug } } })
	)
});
