import { describe, expect, it } from 'vitest';
import { OG_FALLBACK, previewImage } from './seo';

const ORIGIN = 'https://example.com';
const image = {
	url: '/media/content/x/w1920.webp',
	srcset: '/media/content/x/w1920.webp 1920w',
	width: 1920,
	height: 1280,
	alt: 'Кухня на заказ',
	color: '#a07850'
};

describe('previewImage', () => {
	it('AC2: its own photo wins the preview', () => {
		expect(previewImage(ORIGIN, image, 'Кухни')).toEqual({
			url: 'https://example.com/media/content/x/w1920.webp',
			width: 1920,
			height: 1280,
			alt: 'Кухня на заказ'
		});
	});

	it('AC2: a page without a photo of its own falls back to the site cover', () => {
		expect(previewImage(ORIGIN, null, 'Политика')).toEqual({
			url: `https://example.com${OG_FALLBACK.path}`,
			width: 1200,
			height: 630,
			alt: 'Политика'
		});
	});

	it('AC2: the cover is absolute even when the origin ends with a slash', () => {
		expect(previewImage(`${ORIGIN}/`, null, 'Главная').url).toBe(
			'https://example.com/og-cover.png'
		);
	});
});
