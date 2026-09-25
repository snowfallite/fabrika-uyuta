import { error } from '@sveltejs/kit';
import { env } from '$env/dynamic/public';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = () => {
	if (env.PUBLIC_APP_ENV === 'production') error(404, 'Не найдено');
};

export const actions: Actions = {
	// Echoes the kitchen-sink form: proves native fields submit without JS.
	default: async ({ request }) => {
		if (env.PUBLIC_APP_ENV === 'production') error(404, 'Не найдено');
		const data = await request.formData();
		return { submitted: Object.fromEntries([...data].map(([key, value]) => [key, String(value)])) };
	}
};
