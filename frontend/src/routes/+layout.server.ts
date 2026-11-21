import { createApi } from '$lib/server/api';
import { apiData } from '$lib/server/load';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ fetch, cookies }) => ({
	settings: await apiData(createApi(fetch).GET('/api/v1/site-settings/')),
	// Read on the server, so a visitor who already pressed OK sees no flash of the notice.
	cookieConsent: cookies.get('cookie_consent') === '1'
});
