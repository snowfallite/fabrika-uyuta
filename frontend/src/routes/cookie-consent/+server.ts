import { redirect } from '@sveltejs/kit';
import { sitePath } from '$lib/domain/url';
import type { RequestHandler } from './$types';

const YEAR_SECONDS = 60 * 60 * 24 * 365;

/**
 * Remembers that the visitor pressed OK in the cookie notice (tech.md, 10.2).
 * Without JS the form lands here and the 303 brings the visitor back to the same page.
 */
export const POST: RequestHandler = async ({ request, cookies }) => {
	// With JS the notice posts an empty body, so a missing form is normal.
	const form = await request.formData().catch(() => null);
	const target = sitePath(form ? String(form.get('redirectTo') ?? '') : null);
	cookies.set('cookie_consent', '1', {
		path: '/',
		maxAge: YEAR_SECONDS,
		httpOnly: true,
		sameSite: 'lax'
	});
	redirect(303, target);
};
