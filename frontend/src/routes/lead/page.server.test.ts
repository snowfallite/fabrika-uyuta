import { describe, expect, it, vi } from 'vitest';

vi.mock('$env/dynamic/private', () => ({
	env: { API_INTERNAL_URL: 'http://backend:8000', INTERNAL_API_TOKEN: 'internal-token' }
}));

const { actions, load } = await import('./+page.server');
type ActionEvent = Parameters<NonNullable<typeof actions.default>>[0];
const submit = (e: ActionEvent) => actions.default!(e);

function event(fetchImpl: typeof fetch, form: Record<string, string>) {
	const body = new FormData();
	for (const [key, value] of Object.entries(form)) body.set(key, value);
	return {
		request: new Request('http://localhost/lead', { method: 'POST', body }),
		fetch: fetchImpl,
		getClientAddress: () => '203.0.113.7'
	} as unknown as ActionEvent;
}

const filled = {
	name: 'Тестовый Клиент',
	phone: '+7 (999) 123-45-67',
	product: 'wardrobes',
	dimensions: '2 м',
	comment: 'Дуб',
	consent: 'on',
	website: '',
	source_url: '/catalog/wardrobes?x=1'
};

const json = (status: number, body: unknown) =>
	new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });

describe('/lead action', () => {
	it('AC3, AC6: posts the lead with the internal token and the visitor IP', async () => {
		const fetchMock = vi.fn<typeof fetch>(async () => json(201, { id: 'x' }));

		const result = await submit(event(fetchMock, filled));

		expect(result).toEqual({ success: true });
		const request = fetchMock.mock.calls[0]?.[0] as Request;
		expect(request.method).toBe('POST');
		expect(request.url).toBe('http://backend:8000/api/v1/leads/');
		expect(request.headers.get('X-Internal-Token')).toBe('internal-token');
		expect(request.headers.get('X-Client-IP')).toBe('203.0.113.7');
		expect(await request.json()).toEqual({
			name: 'Тестовый Клиент',
			phone: '+7 (999) 123-45-67',
			product: 'wardrobes',
			dimensions: '2 м',
			comment: 'Дуб',
			consent: true,
			website: '',
			source_url: '/catalog/wardrobes?x=1'
		});
	});

	it('sends consent false when the box is not checked', async () => {
		const fetchMock = vi.fn<typeof fetch>(async () => json(201, { id: 'x' }));
		await submit(event(fetchMock, { ...filled, consent: '' }));
		const request = fetchMock.mock.calls[0]?.[0] as Request;
		expect((await request.json()).consent).toBe(false);
	});

	it('keeps the values and reports throttling on 429', async () => {
		const result = await submit(event(async () => json(429, { detail: 'slow down' }), filled));
		expect(result).toMatchObject({
			status: 429,
			data: { status: 'throttled', values: { name: 'Тестовый Клиент', consent: true } }
		});
	});

	it('AC7: maps a 400 to field errors and keeps the values', async () => {
		const result = await submit(
			event(
				async () => json(400, { name: ['Укажите ФИО'], phone: ['Проверьте номер телефона'] }),
				filled
			)
		);
		expect(result).toMatchObject({
			status: 400,
			data: {
				errors: { name: 'Укажите ФИО', phone: 'Проверьте номер телефона' },
				values: { name: 'Тестовый Клиент', product: 'wardrobes' }
			}
		});
	});

	it.each([
		['a 400 without field errors', async () => json(400, [])],
		['a 500', async () => json(500, {})],
		[
			'a network error',
			async () => {
				throw new TypeError('fetch failed');
			}
		]
	])('reports unavailable on %s', async (_, fetchImpl) => {
		const result = await submit(event(fetchImpl as typeof fetch, filled));
		expect(result).toMatchObject({ status: 503, data: { status: 'unavailable' } });
	});
});

describe('/lead load', () => {
	const url = (query: string) => ({ url: new URL(`http://localhost/lead${query}`) });

	it('AC5: preselects a known kind', () => {
		expect(load(url('?product=wardrobes') as never)).toEqual({ product: 'wardrobes' });
	});

	it('AC5: ignores an unknown kind', () => {
		expect(load(url('?product=spaceship') as never)).toEqual({ product: '' });
		expect(load(url('') as never)).toEqual({ product: '' });
	});
});
