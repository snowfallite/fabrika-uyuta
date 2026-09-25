import { expect, test, type Page } from '@playwright/test';

async function fillInvalid(page: Page) {
	const form = page.locator('#lead');
	await form.getByLabel('ФИО').fill('1');
	await form.getByLabel('Телефон').fill('12345');
	await form.getByLabel('Что хотите заказать').selectOption('kitchens');
	await form.getByLabel('Комментарий').fill('Сохранится после ошибки');
	await form.getByRole('checkbox', { name: /согласие/ }).check();
	await form.getByRole('button', { name: 'Отправить заявку' }).click();
}

async function expectFieldErrors(page: Page) {
	const name = page.getByLabel('ФИО');
	const phone = page.getByLabel('Телефон');
	await expect(name).toHaveAttribute('aria-invalid', 'true');
	await expect(name).toHaveAccessibleDescription('Укажите ФИО');
	await expect(phone).toHaveAttribute('aria-invalid', 'true');
	await expect(phone).toHaveAccessibleDescription('Проверьте номер телефона');
	await expect(page.getByLabel('Комментарий')).toHaveValue('Сохранится после ошибки');
	await expect(page.getByLabel('Что хотите заказать')).toHaveValue('kitchens');
	await expect(name).toBeFocused();
}

test.describe('lead errors with JavaScript', () => {
	test('AC7: a 400 shows errors under the fields and focuses the first one', async ({ page }) => {
		await page.goto('/', { waitUntil: 'networkidle' });
		await fillInvalid(page);
		await expectFieldErrors(page);
		expect(new URL(page.url()).pathname).toBe('/');
	});

	test('AC8: a network error shows the alert from 12.2', async ({ page }) => {
		await page.route('**/lead', (route) =>
			route.request().method() === 'POST' ? route.abort('failed') : route.continue()
		);
		await page.goto('/', { waitUntil: 'networkidle' });
		const form = page.locator('#lead');
		await form.getByLabel('ФИО').fill('Тест Клиент');
		await form.getByLabel('Телефон').fill('9991234567');
		await form.getByLabel('Что хотите заказать').selectOption('office');
		await form.getByRole('checkbox', { name: /согласие/ }).check();
		await form.getByRole('button', { name: 'Отправить заявку' }).click();

		await expect(form.getByRole('alert')).toContainText(
			'Не получилось отправить заявку. Попробуйте ещё раз или позвоните нам.'
		);
		await expect(form.getByLabel('ФИО')).toHaveValue('Тест Клиент');
	});

	test('AC9: the button locks while sending and a double click sends once', async ({ page }) => {
		let posts = 0;
		await page.route('**/lead', async (route) => {
			if (route.request().method() !== 'POST') return route.continue();
			posts += 1;
			await new Promise((resolve) => setTimeout(resolve, 800));
			return route.continue();
		});
		await page.goto('/', { waitUntil: 'networkidle' });
		const form = page.locator('#lead');
		await form.getByLabel('ФИО').fill('Тест Двойной');
		await form.getByLabel('Телефон').fill('9991234567');
		await form.getByLabel('Что хотите заказать').selectOption('kitchens');
		await form.getByRole('checkbox', { name: /согласие/ }).check();

		const button = form.getByRole('button', { name: 'Отправить заявку' });
		await button.dblclick();
		await expect(form.getByRole('button', { name: 'Отправляем…' })).toBeDisabled();
		await expect(form.getByRole('status')).toBeVisible();
		expect(posts).toBe(1);
	});
});

test.describe('lead errors without JavaScript', () => {
	test.use({ javaScriptEnabled: false });

	test('AC7: /lead renders the errors, keeps the values and focuses the first field', async ({
		page
	}) => {
		await page.goto('/');
		await fillInvalid(page);
		await expect(page).toHaveURL(/\/lead$/);
		await expectFieldErrors(page);
	});
});
