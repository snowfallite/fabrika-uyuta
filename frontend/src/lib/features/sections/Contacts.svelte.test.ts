import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import type { SiteSettings } from '$lib/types';
import Contacts from './Contacts.svelte';

const empty: SiteSettings = {
	phone: '',
	phone_display: '',
	max_phone: '',
	max_phone_display: '',
	vk_url: '',
	email: '',
	address: '',
	work_hours: '',
	map_url: '',
	social_links: []
};

describe('Contacts', () => {
	it('AC3: empty settings leave no contact cards, labels or undefined', async () => {
		const screen = await render(Contacts, { settings: empty });
		const text = screen.container.textContent ?? '';
		for (const label of ['Телефон', 'MAX', 'Email', 'Адрес', 'Часы работы', 'Открыть на карте']) {
			expect(text).not.toContain(label);
		}
		expect(text).not.toContain('undefined');
		expect(screen.container.querySelector('a[href^="tel:"], a[href^="mailto:"]')).toBeNull();
		await expect.element(screen.getByRole('link', { name: 'Заказать мебель' })).toBeVisible();
	});

	it('AC3: shows only the filled fields', async () => {
		const screen = await render(Contacts, {
			settings: { ...empty, address: 'Вологда', work_hours: 'Пн–Пт, 9:00–18:00' }
		});
		await expect.element(screen.getByText('Вологда')).toBeVisible();
		await expect.element(screen.getByText('Пн–Пт, 9:00–18:00')).toBeVisible();
		expect(screen.container.textContent).not.toContain('Телефон');
		expect(screen.container.textContent).not.toContain('Открыть на карте');
	});

	it('AC2: the phone is a tel: link with E.164 and display text', async () => {
		const screen = await render(Contacts, {
			settings: {
				...empty,
				phone: '+78172000000',
				phone_display: '+7 (817) 200-00-00',
				address: 'Вологда',
				map_url: 'https://yandex.ru/maps/?text=Vologda',
				social_links: [{ label: 'ВКонтакте', url: 'https://vk.com/' }]
			}
		});
		await expect
			.element(screen.getByRole('link', { name: '+7 (817) 200-00-00' }))
			.toHaveAttribute('href', 'tel:+78172000000');
		await expect
			.element(screen.getByRole('link', { name: 'Открыть на карте' }))
			.toHaveAttribute('href', 'https://yandex.ru/maps/?text=Vologda');
		await expect.element(screen.getByRole('link', { name: 'ВКонтакте' })).toBeVisible();
	});

	it('shows the MAX number as text, not as a link', async () => {
		const screen = await render(Contacts, {
			settings: { ...empty, max_phone: '+79990000001', max_phone_display: '+7 (999) 000-00-01' }
		});
		await expect.element(screen.getByText('MAX')).toBeVisible();
		await expect.element(screen.getByText('+7 (999) 000-00-01')).toBeVisible();
		expect(screen.container.querySelector('a[href*="79990000001"]')).toBeNull();
	});
});
