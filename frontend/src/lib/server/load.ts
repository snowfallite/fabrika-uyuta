import { error } from '@sveltejs/kit';

type ApiResult<T> = { data?: T; response: Response };

/** Unwraps an API call for load: 404 passes through, network errors and the rest become 503. */
export async function apiData<T>(call: Promise<ApiResult<T>>): Promise<T> {
	let result: ApiResult<T>;
	try {
		result = await call;
	} catch {
		error(503, 'API недоступен');
	}
	if (result.data !== undefined) return result.data;
	if (result.response.status === 404) error(404, 'Не найдено');
	error(503, 'API недоступен');
}
