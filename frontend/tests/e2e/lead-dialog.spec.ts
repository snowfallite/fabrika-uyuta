import { expect, test } from '@playwright/test';
import { expectNoSeriousA11yViolations } from './axe';
import { SUCCESS, fillLeadForm, onlyRowNamed, uniqueName } from './lead-helpers';

test.describe('lead dialog', () => {
	test('AC1: the hero CTA opens the form, focuses the first field, Esc returns focus', async ({
		page
	}) => {
		await page.goto('/', { waitUntil: 'networkidle' });
		const cta = page.locator('#hero').getByRole('link', { name: 'Оставить заявку' });
		await cta.click();

		const dialog = page.getByRole('dialog', { name: 'Оставить заявку' });
		await expect(dialog).toBeVisible();
		await expect(dialog.getByLabel('ФИО')).toBeFocused();
		expect(new URL(page.url()).pathname).toBe('/');

		await page.keyboard.press('Escape');
		await expect(dialog).toBeHidden();
		await expect(cta).toBeFocused();
	});

	test('AC1: the header CTA opens it and the close button returns focus', async ({
		page,
		viewport
	}) => {
		test.skip((viewport?.width ?? 0) < 640, 'the header CTA shows from 640 px');
		await page.goto('/', { waitUntil: 'networkidle' });
		const cta = page.getByRole('banner').getByRole('link', { name: 'Оставить заявку' });
		await cta.click();
		const dialog = page.getByRole('dialog', { name: 'Оставить заявку' });
		await expect(dialog).toBeVisible();
		await dialog.getByRole('button', { name: 'Закрыть' }).click();
		await expect(dialog).toBeHidden();
		await expect(cta).toBeFocused();
	});

	test('AC3: success shows in the dialog and reopening starts clean', async ({ page, request }) => {
		await page.goto('/', { waitUntil: 'networkidle' });
		const cta = page.locator('#hero').getByRole('link', { name: 'Оставить заявку' });
		await cta.click();
		const dialog = page.getByRole('dialog', { name: 'Оставить заявку' });
		const name = uniqueName();
		await fillLeadForm(dialog, name, 'sliding-wardrobes');
		await dialog.getByRole('button', { name: 'Отправить заявку' }).click();
		await expect(dialog.getByRole('status')).toHaveText(SUCCESS);

		await page.keyboard.press('Escape');
		await expect(dialog).toBeHidden();
		await cta.click();
		await expect(dialog).toBeVisible();
		await expect(dialog.getByLabel('ФИО')).toHaveValue('');
		await expect(dialog.getByRole('checkbox', { name: /согласие/ })).not.toBeChecked();
		expect((await onlyRowNamed(request, name))[4]).toBe('Шкафы-купе');
	});

	test('axe finds no serious issues in the open dialog', async ({ page }) => {
		await page.goto('/', { waitUntil: 'networkidle' });
		await page.locator('#hero').getByRole('link', { name: 'Оставить заявку' }).click();
		await expect(page.getByRole('dialog')).toBeVisible();
		await expectNoSeriousA11yViolations(page);
	});
});

test.describe('lead CTA without JavaScript', () => {
	test.use({ javaScriptEnabled: false });

	test('AC2: the CTA is a plain link to /lead', async ({ page }) => {
		await page.goto('/');
		await page.locator('#hero').getByRole('link', { name: 'Оставить заявку' }).click();
		await expect(page).toHaveURL(/\/lead$/);
		await expect(page.getByRole('heading', { level: 1, name: 'Оставить заявку' })).toBeVisible();
	});
});
