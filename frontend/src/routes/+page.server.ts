import { createApi } from '$lib/server/api';
import { apiData } from '$lib/server/load';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => ({
	home: await apiData(createApi(fetch).GET('/api/v1/home/'))
});
