import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import OtherCategories from './OtherCategories.svelte';

const options = [
	{ value: 'kitchens', label: 'Кухни под заказ' },
	{ value: 'office', label: 'Офисная мебель' },
	{ value: 'wardrobes', label: 'Шкафы' }
];

describe('OtherCategories', () => {
	it('AC8: links the other categories and leaves the current one out', async () => {
		const screen = await render(OtherCategories, { current: 'kitchens', options });

		const office = screen.getByRole('link', { name: 'Офисная мебель' });
		await expect.element(office).toBeVisible();
		expect(office.element().getAttribute('href')).toBe('/catalog/office');
		await expect.element(screen.getByRole('link', { name: 'Шкафы' })).toBeVisible();
		expect(screen.container.textContent).not.toContain('Кухни под заказ');
	});

	it('AC8: a single category leaves no block at all', async () => {
		const screen = await render(OtherCategories, {
			current: 'kitchens',
			options: [{ value: 'kitchens', label: 'Кухни под заказ' }]
		});

		expect(screen.container.textContent?.trim()).toBe('');
	});
});
