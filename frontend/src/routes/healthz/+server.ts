import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

const headers = { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' };

/** Monitoring probe: 200 while the backend (database and worker) is healthy. */
export const GET: RequestHandler = async ({ fetch }) => {
	try {
		const response = await fetch(`${env.API_INTERNAL_URL}/healthz`, {
			signal: AbortSignal.timeout(5000)
		});
		if (response.ok) return new Response('ok', { headers });
	} catch {
		// Backend unreachable: report degraded below.
	}
	return new Response('degraded', { status: 503, headers });
};
