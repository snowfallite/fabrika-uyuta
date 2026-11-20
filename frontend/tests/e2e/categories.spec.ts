import { expect, test } from '@playwright/test';
import { expectNoSeriousA11yViolations } from './axe';

const ORDER = [
	'Кухни под заказ',
	'Кухонные столы',
	'Шкафы',
	'Шкафы-купе',
	'Офисная мебель',
	'Другое'
];

test.describe('home: categories', () => {
	test('AC1: published categories render in position order', async ({ page }) => {
		await page.goto('/');
		const titles = page.locator('#catalog article h3');
		await expect(titles).toHaveText(ORDER);
	});

	test('AC1: the seeded "Другое" category has its own card and page', async ({ page }) => {
		await page.goto('/');
		const card = page.locator('#catalog article').filter({ hasText: 'Другое' });
		await expect(card.getByRole('link', { name: 'Другое' })).toHaveAttribute(
			'href',
			'/catalog/other'
		);
		const response = await page.goto('/catalog/other');
		expect(response?.status()).toBe(200);
		await expect(page.getByRole('heading', { level: 1, name: 'Другое' })).toBeVisible();
	});

	test('AC3: a card links to its page, the CTA opens the dialog with the kind', async ({
		page
	}) => {
		await page.goto('/', { waitUntil: 'networkidle' });
		const card = page.locator('#catalog article').filter({ hasText: 'Шкафы-купе' });
		await expect(card.getByRole('link', { name: 'Шкафы-купе' })).toHaveAttribute(
			'href',
			'/catalog/sliding-wardrobes'
		);
		await card.getByRole('link', { name: 'Оставить заявку' }).click();
		const dialog = page.getByRole('dialog', { name: 'Оставить заявку' });
		await expect(dialog).toBeVisible();
		// S2-03 AC4: open(product) preselects the kind.
		await expect(dialog.getByLabel('Что хотите заказать')).toHaveValue('sliding-wardrobes');
	});

	test('S2-19 AC1: on a phone the text sits under the photo', async ({ page }, testInfo) => {
		test.skip(testInfo.project.name !== 'mobile', 'phone layout');
		await page.goto('/', { waitUntil: 'networkidle' });
		const card = page.locator('#catalog article').first();
		await card.scrollIntoViewIfNeeded();

		const photo = await card.locator('img').first().boundingBox();
		const title = await card.getByRole('heading', { level: 3 }).boundingBox();
		const cta = await card.getByRole('link', { name: 'Оставить заявку' }).boundingBox();
		expect(photo && title && cta).toBeTruthy();
		// The photo ends before the text starts: nothing covers it.
		expect(photo!.y + photo!.height).toBeLessThanOrEqual(title!.y);
		expect(title!.y + title!.height).toBeLessThanOrEqual(cta!.y);
		await expect(card.locator('p')).toBeVisible();
	});

	test('S2-19 AC2: on desktop the text overlays the photo and the description waits for hover', async ({
		page
	}, testInfo) => {
		test.skip(testInfo.project.name !== 'desktop', 'desktop layout');
		await page.goto('/', { waitUntil: 'networkidle' });
		const card = page.locator('#catalog article').first();
		await card.scrollIntoViewIfNeeded();

		const photo = await card.locator('img').first().boundingBox();
		const title = await card.getByRole('heading', { level: 3 }).boundingBox();
		expect(title!.y).toBeGreaterThan(photo!.y);
		expect(title!.y).toBeLessThan(photo!.y + photo!.height);

		const description = card.locator('p');
		await expect(description).toBeHidden();
		await card.hover();
		await expect(description).toBeVisible();
	});

	test('axe finds no serious issues in the catalog section', async ({ page }) => {
		await page.goto('/', { waitUntil: 'networkidle' });
		await page.locator('#catalog').scrollIntoViewIfNeeded();
		await expectNoSeriousA11yViolations(page);
	});
});

test.describe('home: categories without JavaScript', () => {
	test.use({ javaScriptEnabled: false });

	test('AC3: the card CTA goes to /lead with the kind preselected', async ({ page }) => {
		await page.goto('/');
		const card = page.locator('#catalog article').filter({ hasText: 'Офисная мебель' });
		await card.getByRole('link', { name: 'Оставить заявку' }).click();
		await expect(page).toHaveURL(/\/lead\?product=office$/);
		await expect(page.getByLabel('Что хотите заказать')).toHaveValue('office');
	});
});
