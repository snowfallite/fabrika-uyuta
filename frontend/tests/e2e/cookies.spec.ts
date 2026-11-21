import { expect, test } from '@playwright/test';
import { expectNoSeriousA11yViolations } from './axe';

// These tests need a visitor who has not pressed OK yet, so they drop the shared cookie.
test.use({ storageState: { cookies: [], origins: [] } });

const NOTICE = 'Уведомление об использовании cookie';
const COOKIES_LINK = 'Политика использования cookie';

test.describe('cookies page', () => {
	test('AC3: the page describes Metrika and links the other documents', async ({ page }) => {
		const response = await page.goto('/cookies');
		expect(response?.status()).toBe(200);

		await expect(page.getByRole('heading', { level: 1 })).toHaveText(COOKIES_LINK);
		const main = page.locator('main');
		await expect(main).toContainText('Яндекс.Метрика');
		await expect(main).toContainText('ООО «Яндекс»');
		await expect(main).toContainText('cookie_consent');
		await expect(
			main.getByRole('link', { name: 'Политика обработки персональных данных' })
		).toHaveAttribute('href', '/privacy');
		await expect(
			main.getByRole('link', { name: 'Согласие на обработку персональных данных' })
		).toHaveAttribute('href', '/consent');
	});

	test('AC3: the sitemap and the footer point at the page', async ({ page, request, baseURL }) => {
		const origin = new URL(baseURL ?? 'http://localhost:8080').origin;
		const xml = await (await request.get('/sitemap.xml')).text();
		expect(xml).toContain(`<loc>${origin}/cookies</loc>`);

		await page.goto('/');
		await expect(
			page.getByRole('contentinfo').getByRole('link', { name: COOKIES_LINK })
		).toHaveAttribute('href', '/cookies');
	});
});

test.describe('cookie notice', () => {
	test('AC4: the notice shows until OK and stays away afterwards', async ({ page }) => {
		await page.goto('/');
		const notice = page.getByRole('region', { name: NOTICE });
		await expect(notice).toBeVisible();
		await expect(notice).toContainText('Яндекс.Метрика');
		await expect(notice.getByRole('link', { name: 'cookie', exact: true })).toHaveAttribute(
			'href',
			'/cookies'
		);

		const stored = page.waitForResponse((response) => response.url().includes('/cookie-consent'));
		await notice.getByRole('button', { name: 'ОК' }).click();
		await stored;
		await expect(notice).toBeHidden();

		await page.goto('/privacy');
		await expect(page.getByRole('region', { name: NOTICE })).toBeHidden();
		await page.reload();
		await expect(page.getByRole('region', { name: NOTICE })).toBeHidden();
	});

	test('AC6: a foreign redirectTo lands on the home page, GET is not allowed', async ({
		request,
		baseURL
	}) => {
		const origin = new URL(baseURL ?? 'http://localhost:8080').origin;
		const posted = await request.post('/cookie-consent', {
			form: { redirectTo: 'https://evil.test/x' },
			headers: { origin },
			maxRedirects: 0
		});
		expect(posted.status()).toBe(303);
		expect(posted.headers()['location']).toBe('/');

		const got = await request.get('/cookie-consent', { maxRedirects: 0 });
		expect(got.status()).toBe(405);
	});

	test('AC7: nothing reaches mc.yandex.ru while the counter id is empty', async ({ page }) => {
		const hits: string[] = [];
		page.on('request', (request) => {
			if (request.url().includes('mc.yandex.ru')) hits.push(request.url());
		});

		await page.goto('/', { waitUntil: 'networkidle' });

		expect(hits).toEqual([]);
		expect(await page.locator('script[src*="mc.yandex.ru"]').count()).toBe(0);
	});

	test('AC8: the notice leaves the footer links reachable and axe clean', async ({ page }) => {
		const violations: string[] = [];
		page.on('console', (message) => {
			if (message.text().includes('Content Security Policy')) violations.push(message.text());
		});

		await page.goto('/', { waitUntil: 'networkidle' });
		await expect(page.getByRole('region', { name: NOTICE })).toBeVisible();

		// The notice is sticky, so the end of the page frees the footer: the click must land.
		await page.getByRole('contentinfo').getByRole('link', { name: COOKIES_LINK }).click();
		await expect(page).toHaveURL(/\/cookies$/);

		await expect(page.getByRole('region', { name: NOTICE })).toBeVisible();
		await expectNoSeriousA11yViolations(page);
		expect(violations).toEqual([]);
	});
});

test.describe('cookie notice without JS', () => {
	test.use({ javaScriptEnabled: false });

	test('AC5: the OK button posts the form and the 303 returns to the same page', async ({
		page,
		context
	}) => {
		await page.goto('/privacy');
		const notice = page.getByRole('region', { name: NOTICE });
		await expect(notice).toBeVisible();

		await notice.getByRole('button', { name: 'ОК' }).click();

		await expect(page).toHaveURL(/\/privacy$/);
		await expect(page.getByRole('region', { name: NOTICE })).toBeHidden();

		const cookie = (await context.cookies()).find((item) => item.name === 'cookie_consent');
		expect(cookie?.value).toBe('1');
		const halfYear = Date.now() / 1000 + 60 * 60 * 24 * 180;
		expect(cookie?.expires ?? 0).toBeGreaterThan(halfYear);
	});
});
