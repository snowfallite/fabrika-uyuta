import { fail } from '@sveltejs/kit';
import { readLeadForm, type LeadFailure } from '$lib/features/lead-form/lead-form';
import { isProductKind } from '$lib/domain/product-kind';
import { createApi } from '$lib/server/api';
import type { ProductKind } from '$lib/types';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = ({ url }) => {
	const product = url.searchParams.get('product');
	return { product: isProductKind(product) ? product : ('' as const) };
};

export const actions: Actions = {
	// The receiver of every lead form on the site, with or without JS (tech.md, 10.1).
	default: async ({ request, fetch, getClientAddress }) => {
		const { values, website, sourceUrl } = readLeadForm(await request.formData());
		const failure = (status: number, extra: Partial<LeadFailure> = {}) =>
			fail(status, { values, errors: {}, ...extra } satisfies LeadFailure);

		try {
			const { response } = await createApi(fetch, getClientAddress()).POST('/api/v1/leads/', {
				body: {
					...values,
					// The API validates the kind; a wrong value comes back as a 400.
					product: values.product as ProductKind,
					website,
					source_url: sourceUrl
				}
			});
			if (response.status === 201) return { success: true as const };
			if (response.status === 429) return failure(429, { status: 'throttled' });
		} catch {
			// Network error or timeout: same message as a 5xx.
		}
		return failure(503, { status: 'unavailable' });
	}
};
