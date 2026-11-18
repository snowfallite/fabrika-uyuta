import { page } from 'vitest/browser';
import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import type { GalleryItem } from '$lib/types';
import Lightbox from './Lightbox.svelte';

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

describe('Lightbox', () => {
	it('AC6: the open photo names its category from the API', async () => {
		await render(Lightbox, { items: [work], open: true, index: 0 });
		await expect.element(page.getByText('Детская мебель')).toBeVisible();
	});
});
