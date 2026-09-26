import { expect, test } from '@playwright/test';
import { expectNoSeriousA11yViolations } from './axe';

// seed_demo features 4 works on the home page.
test.describe('home: gallery', () => {
	test('AC1, AC4: featured works load lazily with their size', async ({ page }) => {
		await page.goto('/');
		const thumbnails = page.locator('#works li img');
		await expect(thumbnails).toHaveCount(4);
		for (const img of await thumbnails.all()) {
			await expect(img).toHaveAttribute('loading', 'lazy');
			await expect(img).toHaveAttribute('width', /^\d+$/);
			await expect(img).toHaveAttribute('height', /^\d+$/);
		}
	});

	test('AC2: the lightbox shows the widest variant, pages and returns focus', async ({ page }) => {
		await page.goto('/', { waitUntil: 'networkidle' });
		const links = page.locator('#works li a');
		const first = links.nth(0);
		const firstUrl = await first.getAttribute('href');
		const secondUrl = await links.nth(1).getAttribute('href');
		const lastUrl = await links.nth(3).getAttribute('href');

		await first.click();
		const lightbox = page.getByRole('dialog');
		const photo = lightbox.locator('img');
		await expect(photo).toHaveAttribute('src', firstUrl ?? '');

		await lightbox.getByRole('button', { name: 'Вперёд' }).click();
		await expect(photo).toHaveAttribute('src', secondUrl ?? '');
		await page.keyboard.press('ArrowLeft');
		await expect(photo).toHaveAttribute('src', firstUrl ?? '');
		await page.keyboard.press('ArrowLeft');
		await expect(photo).toHaveAttribute('src', lastUrl ?? '');

		await page.keyboard.press('Escape');
		await expect(lightbox).toBeHidden();
		await expect(first).toBeFocused();
	});

	test('axe finds no serious issues with the lightbox open', async ({ page }) => {
		await page.goto('/', { waitUntil: 'networkidle' });
		await page.locator('#works li a').first().click();
		await expect(page.getByRole('dialog')).toBeVisible();
		await expectNoSeriousA11yViolations(page);
	});
});

test.describe('home: gallery without JavaScript', () => {
	test.use({ javaScriptEnabled: false });

	test('AC3: a thumbnail links to the widest variant', async ({ page }) => {
		await page.goto('/');
		const first = page.locator('#works li a').first();
		const href = (await first.getAttribute('href')) ?? '';
		expect(href).toMatch(/^\/media\/content\/[0-9a-f-]+\/w\d+\.webp$/);
		const srcset = (await first.locator('img').getAttribute('srcset')) ?? '';
		const widest = srcset.split(', ').at(-1)?.split(' ')[0];
		expect(href).toBe(widest);
		const response = await page.request.get(href);
		expect(response.headers()['content-type']).toBe('image/webp');
	});
});
