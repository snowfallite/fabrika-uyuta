import { expect, test } from '@playwright/test';
import { expectNoSeriousA11yViolations } from './axe';

const ORDER = ['Кухни под заказ', 'Кухонные столы', 'Шкафы', 'Шкафы-купе', 'Офисная мебель'];

test.describe('home: categories', () => {
	test('AC1: published categories render in position order', async ({ page }) => {
		await page.goto('/');
		const titles = page.locator('#catalog article h3');
		await expect(titles).toHaveText(ORDER);
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
