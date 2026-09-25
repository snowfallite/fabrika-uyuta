import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import type { ImageAsset } from '$lib/types';
import ResponsiveImage from './ResponsiveImage.svelte';

const image: ImageAsset = {
	url: '/media/content/abc/w1280.webp',
	srcset: '/media/content/abc/w640.webp 640w, /media/content/abc/w1280.webp 1280w',
	width: 1280,
	height: 853,
	alt: 'Кухня из дуба',
	color: '#a07850'
};

describe('ResponsiveImage', () => {
	it('renders srcset, sizes, width and height of the widest variant', async () => {
		const screen = await render(ResponsiveImage, { image, sizes: '100vw' });
		const img = screen.getByRole('img', { name: 'Кухня из дуба' });
		await expect.element(img).toHaveAttribute('src', image.url);
		await expect.element(img).toHaveAttribute('srcset', image.srcset);
		await expect.element(img).toHaveAttribute('sizes', '100vw');
		await expect.element(img).toHaveAttribute('width', '1280');
		await expect.element(img).toHaveAttribute('height', '853');
		await expect.element(img).toHaveAttribute('loading', 'lazy');
	});

	it('loads eagerly with high priority when asked', async () => {
		const screen = await render(ResponsiveImage, {
			image,
			sizes: '100vw',
			loading: 'eager',
			fetchpriority: 'high'
		});
		const img = screen.getByRole('img');
		await expect.element(img).toHaveAttribute('loading', 'eager');
		await expect.element(img).toHaveAttribute('fetchpriority', 'high');
	});

	it('renders a hidden placeholder with the aspect ratio when there is no image', async () => {
		const screen = await render(ResponsiveImage, { image: null, sizes: '100vw', aspect: '4/5' });
		expect(screen.container.querySelector('img')).toBeNull();
		const placeholder = screen.container.querySelector<HTMLElement>('div[aria-hidden="true"]');
		expect(placeholder?.style.aspectRatio).toBe('4 / 5');
	});
});
