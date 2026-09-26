import { describe, expect, it } from 'vitest';
import type { SiteSettings } from '$lib/types';
import { furnitureStoreJsonLd } from './json-ld';

const settings: SiteSettings = {
	phone: '+78172000000',
	phone_display: '+7 (817) 200-00-00',
	email: '',
	address: 'Вологда, </script><b>',
	work_hours: '',
	map_url: '',
	social_links: []
};
const image = {
	url: '/media/content/x/w1920.webp',
	srcset: '',
	width: 1920,
	height: 1280,
	alt: '',
	color: '#a07850'
};

describe('furnitureStoreJsonLd', () => {
	it('AC4: parses and carries name, url, telephone, address and image', () => {
		const raw = furnitureStoreJsonLd('https://example.com', settings, image);
		expect(raw).not.toContain('</script>');
		expect(JSON.parse(raw)).toEqual({
			'@context': 'https://schema.org',
			'@type': 'FurnitureStore',
			name: 'Фабрика Уюта',
			url: 'https://example.com/',
			telephone: '+78172000000',
			address: 'Вологда, </script><b>',
			image: 'https://example.com/media/content/x/w1920.webp'
		});
	});

	it('leaves empty contacts and a missing photo out', () => {
		const data = JSON.parse(
			furnitureStoreJsonLd('https://example.com', { ...settings, phone: '', address: '' }, null)
		);
		expect(Object.keys(data)).toEqual(['@context', '@type', 'name', 'url']);
	});
});
