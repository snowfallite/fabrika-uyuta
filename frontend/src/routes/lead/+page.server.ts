import { fail } from '@sveltejs/kit';
import { readLeadForm, type LeadFailure } from '$lib/features/lead-form/lead-form';
import { mapLeadErrors } from '$lib/domain/lead-errors';
import { createApi } from '$lib/server/api';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = ({ url }) => {
	// A category slug is at most 32 characters (tech.md, 6); the form drops a kind its list
	// does not offer, so an old or hidden slug just leaves the placeholder.
	return { product: (url.searchParams.get('product') ?? '').slice(0, 32) };
};

export const actions: Actions = {
	// The receiver of every lead form on the site, with or without JS (tech.md, 10.1).
	default: async ({ request, fetch, getClientAddress }) => {
		const { values, website, sourceUrl } = readLeadForm(await request.formData());
		const failure = (status: number, extra: Partial<LeadFailure> = {}) =>
			fail(status, { values, errors: {}, ...extra } satisfies LeadFailure);

		try {
			const { response, error } = await createApi(fetch, getClientAddress()).POST(
				'/api/v1/leads/',
				{
					body: {
						...values,
						website,
						source_url: sourceUrl
					}
				}
			);
			if (response.status === 201) return { success: true as const };
			if (response.status === 429) return failure(429, { status: 'throttled' });
			const errors = response.status === 400 ? mapLeadErrors(error) : {};
			if (Object.keys(errors).length > 0) return failure(400, { errors });
		} catch {
			// Network error or timeout: same message as a 5xx.
		}
		return failure(503, { status: 'unavailable' });
	}
};
