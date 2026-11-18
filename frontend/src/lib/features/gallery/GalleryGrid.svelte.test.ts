import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import type { GalleryItem } from '$lib/types';
import GalleryGrid from './GalleryGrid.svelte';

const work: GalleryItem = {
	id: 1,
	category: 'kids',
	category_title: 'Детская мебель',
	title: 'Кровать-чердак',
	caption: '',
	image: {
		url: '/media/content/x/w1200.webp',
		srcset: '/media/content/x/w640.webp 640w, /media/content/x/w1200.webp 1200w',
		width: 1200,
		height: 900,
		alt: 'Кровать-чердак',
		color: '#a07850'
	}
};

describe('GalleryGrid', () => {
	it('AC6: a thumbnail wears the category title the API sent', async () => {
		const screen = await render(GalleryGrid, { items: [work] });
		await expect.element(screen.getByText('Детская мебель')).toBeVisible();
		await expect.element(screen.getByText('Кровать-чердак')).toBeVisible();
	});
});
