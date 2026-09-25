import createClient from 'openapi-fetch';
import type { paths } from '$lib/types/api';
import { env } from '$env/dynamic/private';

const TIMEOUT_MS = 5000;

export function createApi(fetchFn: typeof fetch, clientIp?: string) {
	return createClient<paths>({
		baseUrl: env.API_INTERNAL_URL,
		// SvelteKit event.fetch; every request gets a 5 s timeout (tech.md, 10.3).
		fetch: (request: Request) =>
			fetchFn(new Request(request, { signal: AbortSignal.timeout(TIMEOUT_MS) })),
		headers: {
			'X-Internal-Token': env.INTERNAL_API_TOKEN,
			...(clientIp ? { 'X-Client-IP': clientIp } : {})
		}
	});
}
