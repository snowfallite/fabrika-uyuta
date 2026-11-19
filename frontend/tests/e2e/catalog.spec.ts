import { expect, test } from '@playwright/test';
import { expectNoSeriousA11yViolations } from './axe';
import { SUCCESS, fillLeadForm, onlyRowNamed, uniqueName } from './lead-helpers';

// seed_demo: kitchens has two description paragraphs and four works in this order.
const KITCHEN_WORKS = [
	'Кухня «Тёплый орех»',
	'Угловая кухня',
	'Светлая кухня с островом',
	'Кухня в стиле лофт'
];

test.describe('/catalog/<slug>', () => {
	test('AC1: a published category shows title, description and its works in order', async ({
		page
	}) => {
		const response = await page.goto('/catalog/kitchens');
		expect(response?.status()).toBe(200);
		await expect(page.getByRole('heading', { level: 1 })).toHaveText('Кухни под заказ');
		await expect(page.getByTestId('description').locator('p')).toHaveCount(2);
		await expect(page.locator('#category-works li span.font-display')).toHaveText(KITCHEN_WORKS);
	});

	test('AC2: an unknown slug is a 404 page', async ({ page }) => {
		const response = await page.goto('/catalog/spaceship');
		expect(response?.status()).toBe(404);
		await expect(page.getByRole('heading', { name: 'Страница не найдена' })).toBeVisible();
	});

	test('AC3: title, description, canonical and OG image are set with absolute URLs', async ({
		page,
		baseURL
	}) => {
		await page.goto('/catalog/kitchens');
		await expect(page).toHaveTitle('Кухни под заказ | Фабрика Уюта');
		const head = page.locator('head');
		await expect(head.locator('meta[name="description"]')).toHaveAttribute(
			'content',
			'Кухонные гарнитуры по индивидуальным размерам.'
		);
		const origin = new URL(baseURL ?? 'http://localhost:8080').origin;
		await expect(head.locator('link[rel="canonical"]')).toHaveAttribute(
			'href',
			`${origin}/catalog/kitchens`
		);
		await expect(head.locator('meta[property="og:image"]')).toHaveAttribute(
			'content',
			new RegExp(`^${origin}/media/content/[0-9a-f-]+/w\\d+\\.webp$`)
		);
	});

	test('AC4: the page form sends the category kind', async ({ page, request }) => {
		await page.goto('/catalog/wardrobes', { waitUntil: 'networkidle' });
		const form = page.locator('#category-lead');
		await expect(form.getByLabel('Что хотите заказать')).toHaveValue('wardrobes');
		const name = uniqueName();
		await form.getByLabel('ФИО').fill(name);
		await form.getByLabel('Телефон').fill('9991234567');
		await form.getByRole('checkbox', { name: /согласие/ }).check();
		await form.getByRole('button', { name: 'Отправить заявку' }).click();
		await expect(form.getByRole('status')).toHaveText(SUCCESS);
		const row = await onlyRowNamed(request, name);
		expect([row[4], row[7]]).toEqual(['Шкафы', '/catalog/wardrobes']);
	});

	test('S2-18 AC8: the page links the other directions and skips its own', async ({ page }) => {
		await page.goto('/catalog/kitchens');

		const others = page.locator('#other-categories');

		await expect(others.getByRole('link', { name: 'Офисная мебель' })).toHaveAttribute(
			'href',
			'/catalog/office'
		);
		await expect(others.getByRole('link', { name: 'Другое' })).toBeVisible();
		await expect(others.getByRole('link', { name: 'Кухни под заказ' })).toHaveCount(0);
	});

	test('axe finds no serious issues on a category page', async ({ page }) => {
		await page.goto('/catalog/kitchens', { waitUntil: 'networkidle' });
		await expectNoSeriousA11yViolations(page);
	});
});

test.describe('/catalog/<slug> without JavaScript', () => {
	test.use({ javaScriptEnabled: false });

	test('AC4: the form works without JS and keeps the kind', async ({ page, request }) => {
		await page.goto('/catalog/office');
		const name = uniqueName();
		await fillLeadForm(page.locator('#category-lead'), name, 'office');
		await page.locator('#category-lead').getByRole('button', { name: 'Отправить заявку' }).click();
		await expect(page.getByRole('status')).toHaveText(SUCCESS);
		expect((await onlyRowNamed(request, name))[4]).toBe('Офисная мебель');
	});
});
