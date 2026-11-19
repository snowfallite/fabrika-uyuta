import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import type { CategorySummary } from '$lib/types';
import CategoryCard from './CategoryCard.svelte';

const base: CategorySummary = {
	slug: 'wardrobes',
	title: 'Шкафы',
	short_description: 'Распашные шкафы под ваши размеры.',
	cover: null,
	updated_at: '2026-11-20T10:00:00Z'
};

describe('CategoryCard', () => {
	it('AC2: without a cover it shows a placeholder, not a broken image', async () => {
		const screen = await render(CategoryCard, { category: base });
		expect(screen.container.querySelector('img')).toBeNull();
		expect(screen.container.querySelector('div[aria-hidden="true"]')).not.toBeNull();
		await expect.element(screen.getByRole('heading', { name: 'Шкафы' })).toBeVisible();
	});

	it('renders the cover with its alt text', async () => {
		const screen = await render(CategoryCard, {
			category: {
				...base,
				cover: {
					url: '/media/content/x/w1200.webp',
					srcset: '/media/content/x/w640.webp 640w, /media/content/x/w1200.webp 1200w',
					width: 1200,
					height: 1500,
					alt: 'Шкафы',
					color: '#a07850'
				}
			}
		});
		const img = screen.getByRole('img', { name: 'Шкафы' });
		await expect.element(img).toHaveAttribute('loading', 'lazy');
		await expect.element(img).toHaveAttribute('width', '1200');
	});

	it('AC1: a category the content manager added carries its own kind', async () => {
		const screen = await render(CategoryCard, {
			category: { ...base, slug: 'kids-rooms', title: 'Детские комнаты' }
		});
		await expect
			.element(screen.getByRole('link', { name: 'Оставить заявку' }))
			.toHaveAttribute('href', '/lead?product=kids-rooms');
	});

	it('AC3: links to the category page and the CTA to /lead with the kind', async () => {
		const screen = await render(CategoryCard, { category: base });
		await expect
			.element(screen.getByRole('link', { name: 'Шкафы' }))
			.toHaveAttribute('href', '/catalog/wardrobes');
		await expect
			.element(screen.getByRole('link', { name: 'Оставить заявку' }))
			.toHaveAttribute('href', '/lead?product=wardrobes');
	});
});
