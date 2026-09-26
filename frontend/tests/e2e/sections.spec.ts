import { expect, test } from '@playwright/test';
import { expectNoSeriousA11yViolations } from './axe';

// tech.md 10.1: anchors in page order.
const ANCHORS = [
	'hero',
	'about',
	'catalog',
	'works',
	'materials',
	'process',
	'advantages',
	'lead',
	'contacts'
];

// seed_demo contacts.
const PHONE = { href: 'tel:+78172000000', text: '+7 (817) 200-00-00' };

test.describe('home: static sections and contacts', () => {
	test('AC1: every template section is on the page in order', async ({ page }) => {
		await page.goto('/');
		const ids = await page
			.locator('main section[id]')
			.evaluateAll((sections) => sections.map((section) => section.id));
		expect(ids).toEqual(ANCHORS);
	});

	test('AC1: menu links scroll to their sections', async ({ page, viewport }) => {
		test.skip((viewport?.width ?? 0) < 1024, 'the desktop menu shows from 1024 px');
		await page.goto('/', { waitUntil: 'networkidle' });
		const menu = page.getByRole('navigation', { name: 'Основное меню' });
		for (const [label, id] of [
			['Материалы', 'materials'],
			['Контакты', 'contacts'],
			['О компании', 'about']
		] as const) {
			await menu.getByRole('link', { name: label }).click();
			await expect(page).toHaveURL(new RegExp(`#${id}$`));
			await expect(page.locator(`#${id}`)).toBeInViewport();
		}
	});

	test('AC2: the phone is a tel: link in the header, the footer and the contacts', async ({
		page,
		viewport
	}) => {
		await page.goto('/');
		const inContacts = page.locator('#contacts').getByRole('link', { name: PHONE.text });
		const inFooter = page.getByRole('contentinfo').getByRole('link', { name: PHONE.text });
		await expect(inContacts).toHaveAttribute('href', PHONE.href);
		await expect(inFooter).toHaveAttribute('href', PHONE.href);
		if ((viewport?.width ?? 0) >= 1280) {
			const inHeader = page.getByRole('banner').getByRole('link', { name: PHONE.text });
			await expect(inHeader).toHaveAttribute('href', PHONE.href);
		}
	});

	test('axe finds no serious issues on the whole home page', async ({ page }) => {
		await page.goto('/', { waitUntil: 'networkidle' });
		await expectNoSeriousA11yViolations(page);
	});
});
