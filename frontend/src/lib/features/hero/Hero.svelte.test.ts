import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import type { ImageAsset } from '$lib/types';
import Hero from './Hero.svelte';

const image: ImageAsset = {
	url: '/media/content/x/w1920.webp',
	srcset: '/media/content/x/w640.webp 640w, /media/content/x/w1920.webp 1920w',
	width: 1920,
	height: 2400,
	alt: 'Кухня из дуба',
	color: '#a07850'
};

describe('Hero', () => {
	it('AC1, AC3: renders the photo eagerly with srcset and size attributes', async () => {
		const screen = await render(Hero, { image });
		const img = screen.getByRole('img', { name: 'Кухня из дуба' });
		await expect.element(img).toHaveAttribute('srcset', image.srcset);
		await expect.element(img).toHaveAttribute('sizes', '(min-width: 1024px) 50vw, 100vw');
		await expect.element(img).toHaveAttribute('width', '1920');
		await expect.element(img).toHaveAttribute('height', '2400');
		await expect.element(img).toHaveAttribute('loading', 'eager');
		await expect.element(img).toHaveAttribute('fetchpriority', 'high');
	});

	it('AC2: an empty slot keeps the heading and CTA and shows a placeholder', async () => {
		const screen = await render(Hero, { image: null });
		await expect
			.element(screen.getByRole('heading', { level: 1, name: 'Мебель на заказ в Вологде' }))
			.toBeVisible();
		await expect
			.element(screen.getByRole('link', { name: 'Оставить заявку' }))
			.toHaveAttribute('href', '/lead');
		expect(screen.container.querySelector('img')).toBeNull();
		expect(screen.container.querySelector('#hero div[aria-hidden="true"]')).not.toBeNull();
	});
});
