import { expect, test } from '@playwright/test';
import { expectNoSeriousA11yViolations } from './axe';

test.describe('/dev/ui kitchen sink', () => {
	test('AC1: shows every primitive in its states', async ({ page }) => {
		// Interactive parts need hydration: wait until the JS bundle has settled.
		await page.goto('/dev/ui', { waitUntil: 'networkidle' });
		for (const name of [
			'Button',
			'Поля и форма',
			'Alert',
			'Dialog и Sheet',
			'ResponsiveImage',
			'Section default',
			'Section muted',
			'Section inverted'
		]) {
			await expect(page.getByRole('heading', { name })).toBeVisible();
		}
		await expect(page.getByRole('button', { name: 'loading' })).toBeDisabled();
		await expect(page.getByRole('button', { name: 'disabled' })).toBeDisabled();
		await expect(page.getByLabel('Поле с ошибкой')).toHaveAttribute('aria-invalid', 'true');
		await expect(page.getByLabel('Отключено')).toBeDisabled();
		await expect(page.getByRole('status').first()).toBeVisible();
		await expect(page.getByRole('alert')).toBeVisible();
		await expect(page.getByRole('img', { name: 'Пример фото' })).toBeVisible();

		await page.getByRole('button', { name: 'Открыть Dialog' }).click();
		await expect(page.getByRole('dialog', { name: 'Заголовок диалога' })).toBeVisible();
		await page.keyboard.press('Escape');
		await page.getByRole('button', { name: 'Открыть Sheet' }).click();
		await expect(page.getByRole('dialog', { name: 'Панель' })).toBeVisible();
	});

	test('AC4: axe finds no serious issues on /dev/ui', async ({ page }) => {
		await page.goto('/dev/ui');
		await expectNoSeriousA11yViolations(page);
	});

	test('AC4: axe finds no serious issues on the error page', async ({ page }) => {
		const response = await page.goto('/no-such-page');
		expect(response?.status()).toBe(404);
		await expect(page.getByRole('heading', { name: 'Страница не найдена' })).toBeVisible();
		await expectNoSeriousA11yViolations(page);
	});
});

test.describe('without JavaScript', () => {
	test.use({ javaScriptEnabled: false });

	test('AC5: native fields submit their values', async ({ page }) => {
		await page.goto('/dev/ui');
		await page.getByLabel('Обычное поле').fill('Тест');
		await page.getByLabel('Телефон').fill('8 999 000 00 01');
		await page.getByLabel('Выбор').selectOption('wardrobes');
		await page.getByLabel('Многострочное поле').fill('Комментарий');
		await page.getByRole('checkbox').check();
		await page.getByRole('button', { name: 'Отправить', exact: true }).click();

		const submitted = JSON.parse((await page.getByTestId('submitted').textContent()) ?? '{}');
		expect(submitted).toMatchObject({
			name: 'Тест',
			phone: '8 999 000 00 01',
			product: 'wardrobes',
			comment: 'Комментарий',
			consent: 'on'
		});
	});
});
