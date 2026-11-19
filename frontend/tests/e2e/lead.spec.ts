import { expect, test } from '@playwright/test';
import { expectNoSeriousA11yViolations } from './axe';
import { SUCCESS, fillLeadForm, onlyRowNamed, uniqueName } from './lead-helpers';

test.describe('lead form with JavaScript', () => {
	test('AC1, AC4, AC6: home form succeeds in place, reaches the sheet, never calls /api/', async ({
		page,
		request
	}) => {
		const apiCalls: string[] = [];
		page.on('request', (r) => {
			if (new URL(r.url()).pathname.startsWith('/api/')) apiCalls.push(r.url());
		});
		await page.goto('/', { waitUntil: 'networkidle' });
		const section = page.locator('#lead');
		const name = uniqueName();

		await fillLeadForm(section, name);
		await section.getByRole('button', { name: 'Отправить заявку' }).click();

		await expect(section.getByRole('status')).toHaveText(SUCCESS);
		expect(new URL(page.url()).pathname).toBe('/');
		await section.getByRole('button', { name: 'Отправить ещё одну' }).click();
		await expect(section.getByLabel('ФИО')).toHaveValue('');
		await expect(section.getByRole('checkbox', { name: /согласие/ })).not.toBeChecked();

		const row = await onlyRowNamed(request, name);
		expect(row).toHaveLength(8);
		expect(row[0]).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
		expect(row[1]).toMatch(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/);
		expect(row.slice(2)).toEqual([
			name,
			'+79991234567',
			'Кухни под заказ',
			'Стена 3 м',
			'=1+1',
			'/'
		]);
		expect(apiCalls).toEqual([]);
	});

	test('AC2: the kind list holds the published categories in their order', async ({ page }) => {
		await page.goto('/lead');

		await expect(page.getByLabel('Что хотите заказать').locator('option')).toHaveText([
			'Выберите',
			'Кухни под заказ',
			'Кухонные столы',
			'Шкафы',
			'Шкафы-купе',
			'Офисная мебель',
			'Другое'
		]);
	});

	test('AC5: /lead preselects a known kind and ignores an unknown one', async ({ page }) => {
		await page.goto('/lead?product=wardrobes');
		await expect(page.getByLabel('Что хотите заказать')).toHaveValue('wardrobes');
		await page.goto('/lead?product=spaceship');
		await expect(page.getByLabel('Что хотите заказать')).toHaveValue('');
	});

	test('axe finds no serious issues on /lead', async ({ page }) => {
		await page.goto('/lead', { waitUntil: 'networkidle' });
		await expectNoSeriousA11yViolations(page);
	});
});

test.describe('lead form without JavaScript', () => {
	test.use({ javaScriptEnabled: false });

	test('AC2: the home form posts to /lead and shows the same success text', async ({
		page,
		request
	}) => {
		await page.goto('/');
		const name = uniqueName();
		await fillLeadForm(page.locator('#lead'), name, 'office');
		await page.locator('#lead').getByRole('button', { name: 'Отправить заявку' }).click();

		await expect(page).toHaveURL(/\/lead$/);
		await expect(page.getByRole('status')).toHaveText(SUCCESS);
		const row = await onlyRowNamed(request, name);
		expect(row[4]).toBe('Офисная мебель');
	});
});
