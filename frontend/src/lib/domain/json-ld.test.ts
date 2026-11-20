import { describe, expect, it } from 'vitest';
import fc from 'fast-check';
import type { CategorySummary, SiteSettings } from '$lib/types';
import { breadcrumbListJsonLd, furnitureStoreJsonLd, itemListJsonLd } from './json-ld';

const numRuns = process.env.CI ? 200 : 50;
const ORIGIN = 'https://example.com';

const settings: SiteSettings = {
	phone: '+78172000000',
	phone_display: '+7 (817) 200-00-00',
	max_phone: '',
	max_phone_display: '',
	vk_url: '',
	email: '',
	city: '',
	address: 'Вологда, </script><b>',
	work_hours: '',
	map_url: '',
	social_links: [],
	product_options: []
};
const image = {
	url: '/media/content/x/w1920.webp',
	srcset: '',
	width: 1920,
	height: 1280,
	alt: '',
	color: '#a07850'
};

const category = (slug: string, title: string): CategorySummary => ({
	slug,
	title,
	short_description: '',
	cover: null,
	updated_at: '2026-11-20T10:00:00Z'
});

describe('furnitureStoreJsonLd', () => {
	it('AC4: parses and carries name, url, telephone, address and image', () => {
		const raw = furnitureStoreJsonLd(ORIGIN, settings, image);
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
			furnitureStoreJsonLd(ORIGIN, { ...settings, phone: '', address: '' }, null)
		);
		expect(Object.keys(data)).toEqual(['@context', '@type', 'name', 'url']);
	});

	it('AC3: the city turns the address into PostalAddress', () => {
		const data = JSON.parse(
			furnitureStoreJsonLd(ORIGIN, { ...settings, city: 'Вологда', address: 'ул. Мира, 1' }, null)
		);
		expect(data.address).toEqual({
			'@type': 'PostalAddress',
			addressLocality: 'Вологда',
			streetAddress: 'ул. Мира, 1'
		});
	});

	it('AC3: the city alone is enough for PostalAddress', () => {
		const data = JSON.parse(
			furnitureStoreJsonLd(ORIGIN, { ...settings, city: 'Вологда', address: '' }, null)
		);
		expect(data.address).toEqual({ '@type': 'PostalAddress', addressLocality: 'Вологда' });
	});

	it('AC3: carries email, the map link and sameAs from VK and the social links', () => {
		const data = JSON.parse(
			furnitureStoreJsonLd(
				ORIGIN,
				{
					...settings,
					email: 'info@example.ru',
					map_url: 'https://yandex.ru/maps/org/1',
					vk_url: 'https://vk.com/fabrikauyuta',
					social_links: [{ label: 'Telegram', url: 'https://t.me/fabrikauyuta' }]
				},
				null
			)
		);
		expect(data.email).toBe('info@example.ru');
		expect(data.hasMap).toBe('https://yandex.ru/maps/org/1');
		expect(data.sameAs).toEqual(['https://vk.com/fabrikauyuta', 'https://t.me/fabrikauyuta']);
	});

	it('AC3: without VK and social links there is no sameAs', () => {
		const data = JSON.parse(furnitureStoreJsonLd(ORIGIN, settings, null));
		expect(data).not.toHaveProperty('sameAs');
	});
});

describe('itemListJsonLd', () => {
	it('AC5: numbers the categories in the given order and links their pages', () => {
		const raw = itemListJsonLd(ORIGIN, [
			category('office', 'Офисная мебель'),
			category('kitchens', 'Кухни под заказ')
		]);
		expect(JSON.parse(raw)).toEqual({
			'@context': 'https://schema.org',
			'@type': 'ItemList',
			itemListElement: [
				{
					'@type': 'ListItem',
					position: 1,
					name: 'Офисная мебель',
					url: 'https://example.com/catalog/office'
				},
				{
					'@type': 'ListItem',
					position: 2,
					name: 'Кухни под заказ',
					url: 'https://example.com/catalog/kitchens'
				}
			]
		});
	});

	it('AC5: an empty catalog gives an empty list', () => {
		expect(JSON.parse(itemListJsonLd(ORIGIN, [])).itemListElement).toEqual([]);
	});
});

describe('breadcrumbListJsonLd', () => {
	it('AC4: the path of a category page keeps its three levels', () => {
		const raw = breadcrumbListJsonLd(ORIGIN, [
			{ label: 'Главная', href: '/' },
			{ label: 'Направления', href: '/#catalog' },
			{ label: 'Шкафы' }
		]);
		expect(JSON.parse(raw).itemListElement).toEqual([
			{
				'@type': 'ListItem',
				position: 1,
				name: 'Главная',
				item: 'https://example.com/',
				url: 'https://example.com/'
			},
			{
				'@type': 'ListItem',
				position: 2,
				name: 'Направления',
				item: 'https://example.com/#catalog',
				url: 'https://example.com/#catalog'
			},
			{ '@type': 'ListItem', position: 3, name: 'Шкафы' }
		]);
	});

	it('AC5: every step but the last carries url beside item', () => {
		fc.assert(
			fc.property(
				fc.array(fc.string({ minLength: 1 }), { minLength: 1, maxLength: 4 }),
				fc.string({ minLength: 1 }),
				(labels, current) => {
					const crumbs = [
						...labels.map((label) => ({ label, href: '/catalog/x' })),
						{ label: current }
					];
					const items: { item?: string; url?: string }[] = JSON.parse(
						breadcrumbListJsonLd(ORIGIN, crumbs)
					).itemListElement;
					for (const entry of items.slice(0, -1)) expect(entry.url).toBe(entry.item);
					expect(items.at(-1)).not.toHaveProperty('url');
				}
			),
			{ numRuns }
		);
	});

	it('AC4: positions run from one and the current page carries no item', () => {
		fc.assert(
			fc.property(
				fc.array(fc.string({ minLength: 1 }), { minLength: 1, maxLength: 4 }),
				fc.string({ minLength: 1 }),
				(labels, current) => {
					const crumbs = [...labels.map((label) => ({ label, href: '/' })), { label: current }];
					const items: { position: number; item?: string }[] = JSON.parse(
						breadcrumbListJsonLd(ORIGIN, crumbs)
					).itemListElement;
					expect(items.map((entry) => entry.position)).toEqual(crumbs.map((_, index) => index + 1));
					expect(items.at(-1)).not.toHaveProperty('item');
					for (const entry of items.slice(0, -1)) expect(entry).toHaveProperty('item');
				}
			),
			{ numRuns }
		);
	});
});
