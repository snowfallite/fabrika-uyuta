import { afterEach, describe, expect, it, vi } from 'vitest';
import { render } from 'vitest-browser-svelte';
import { COOKIE_NOTICE } from '$lib/content/layout';
import CookieNotice from './CookieNotice.svelte';

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('CookieNotice', () => {
	it('AC4: shows the text, the link to /cookies and the OK button', async () => {
		const screen = await render(CookieNotice, { accepted: false, path: '/' });

		const notice = screen.getByRole('region', { name: COOKIE_NOTICE.label });
		await expect.element(notice).toBeVisible();
		await expect
			.element(notice.getByRole('link', { name: COOKIE_NOTICE.linkText }))
			.toHaveAttribute('href', '/cookies');
		await expect.element(notice.getByRole('button', { name: COOKIE_NOTICE.accept })).toBeVisible();
		expect(screen.container.textContent).toContain('Яндекс.Метрика');
	});

	it('AC4: stays away once the visitor pressed OK', async () => {
		const screen = await render(CookieNotice, { accepted: true, path: '/' });
		expect(screen.container.textContent).toBe('');
	});

	it('AC5: the form posts to /cookie-consent and carries the current path', async () => {
		const screen = await render(CookieNotice, { accepted: false, path: '/catalog/office?a=b' });

		const form = screen.container.querySelector('form');
		expect(form?.getAttribute('action')).toBe('/cookie-consent');
		expect(form?.getAttribute('method')?.toLowerCase()).toBe('post');
		const target = screen.container.querySelector<HTMLInputElement>('input[name="redirectTo"]');
		expect(target?.value).toBe('/catalog/office?a=b');
	});

	it('AC4: with JS the click sends the request and hides the notice', async () => {
		const calls: string[] = [];
		vi.stubGlobal('fetch', (input: RequestInfo | URL) => {
			calls.push(String(input));
			return Promise.resolve(new Response(null, { status: 204 }));
		});
		const screen = await render(CookieNotice, { accepted: false, path: '/' });

		await screen.getByRole('button', { name: COOKIE_NOTICE.accept }).click();

		expect(calls).toEqual(['/cookie-consent']);
		expect(screen.container.textContent).toBe('');
	});
});
