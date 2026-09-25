import { expect, type APIRequestContext, type Locator, type Page } from '@playwright/test';

const apiUrl = process.env.E2E_API_URL ?? 'http://localhost:8000';

/** Rows of the fake Google sheet, through the E2E-only backend endpoint. */
async function sheetRows(request: APIRequestContext): Promise<string[][]> {
	const response = await request.get(`${apiUrl}/api/v1/test/fake-sheet/`, {
		headers: { 'X-Internal-Token': process.env.INTERNAL_API_TOKEN ?? '' }
	});
	expect(response.ok()).toBe(true);
	return (await response.json()).rows;
}

/** Waits for the worker and returns the only row with this name. */
export async function onlyRowNamed(request: APIRequestContext, name: string) {
	await expect
		.poll(async () => (await sheetRows(request)).filter((row) => row[2] === name).length, {
			timeout: 20_000
		})
		.toBe(1);
	return (await sheetRows(request)).find((row) => row[2] === name) ?? [];
}

export const uniqueName = () => `Тест Клиент ${Date.now()}${Math.floor(Math.random() * 1000)}`;

export async function fillLeadForm(scope: Page | Locator, name: string, product = 'kitchens') {
	await scope.getByLabel('ФИО').fill(name);
	await scope.getByLabel('Телефон').fill('9991234567');
	await scope.getByLabel('Что хотите заказать').selectOption(product);
	await scope.getByLabel('Примерные размеры').fill('Стена 3 м');
	await scope.getByLabel('Комментарий').fill('=1+1');
	await scope.getByRole('checkbox', { name: /согласие/ }).check();
}

export const SUCCESS = 'Спасибо! Заявка принята. Перезвоним в рабочее время.';
