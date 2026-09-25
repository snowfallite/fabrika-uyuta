import { createApi } from '$lib/server/api';
import { apiData } from '$lib/server/load';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ fetch }) => ({
	settings: await apiData(createApi(fetch).GET('/api/v1/site-settings/'))
});
