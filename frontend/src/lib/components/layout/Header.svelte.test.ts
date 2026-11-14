import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import type { SiteSettings } from '$lib/types';
import Footer from './Footer.svelte';
import Header from './Header.svelte';

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
const filled: SiteSettings = {
	...empty,
	phone: '+79991234567',
	phone_display: '+7 (999) 123-45-67',
	email: 'info@example.ru',
	address: 'Вологда'
};
const nav = [
	{ label: 'Раздел А', href: '/#a' },
	{ label: 'Раздел Б', href: '/#b' }
];

describe('Header and Footer', () => {
	it('AC2: build the menu from the nav prop', async () => {
		const screen = await render(Header, { settings: empty, nav });
		const menu = screen.getByRole('navigation', { name: 'Основное меню' });
		await expect
			.element(menu.getByRole('link', { name: 'Раздел А' }))
			.toHaveAttribute('href', '/#a');
		await expect
			.element(menu.getByRole('link', { name: 'Раздел Б' }))
			.toHaveAttribute('href', '/#b');
	});

	it('AC7: empty settings hide the phone in the header', async () => {
		const screen = await render(Header, { settings: empty, nav });
		expect(screen.container.querySelector('a[href^="tel:"]')).toBeNull();
	});

	it('AC7: a phone shows as a tel: link with E.164 and display text', async () => {
		const screen = await render(Header, { settings: filled, nav });
		const link = screen.container.querySelector('a[href^="tel:"]');
		expect(link?.getAttribute('href')).toBe('tel:+79991234567');
		expect(link?.textContent?.trim()).toBe('+7 (999) 123-45-67');
	});

	it('AC7: empty settings leave no contact rows in the footer', async () => {
		const screen = await render(Footer, { settings: empty, nav });
		expect(screen.container.querySelector('a[href^="tel:"]')).toBeNull();
		expect(screen.container.querySelector('a[href^="mailto:"]')).toBeNull();
		expect(screen.container.textContent).not.toContain('undefined');
		expect(screen.container.querySelectorAll('li:empty')).toHaveLength(0);
	});

	it('AC7: filled settings show phone, email and address in the footer', async () => {
		const screen = await render(Footer, { settings: filled, nav });
		await expect.element(screen.getByRole('link', { name: '+7 (999) 123-45-67' })).toBeVisible();
		await expect.element(screen.getByRole('link', { name: 'info@example.ru' })).toBeVisible();
		await expect.element(screen.getByText('Вологда')).toBeVisible();
	});
});
