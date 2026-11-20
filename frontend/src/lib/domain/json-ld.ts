import type { CategorySummary, ImageAsset, SiteSettings } from '$lib/types';
import { absoluteUrl } from './url';

/** One step of the visible breadcrumbs and of the markup; the current page carries no href. */
export type Crumb = { label: string; href?: string };

/** "<" escaped: every block sits inside a <script> element. */
const encode = (data: unknown): string => JSON.stringify(data).replace(/</g, '\\u003c');

/** The city is a field of its own, so the markup can carry addressLocality (tech.md, v16). */
function postalAddress(settings: SiteSettings): object | string | undefined {
	if (!settings.city) return settings.address || undefined;
	return {
		'@type': 'PostalAddress',
		addressLocality: settings.city,
		...(settings.address && { streetAddress: settings.address })
	};
}

/** FurnitureStore structured data for the home page (tech.md, S2-11, S2-18); empty fields stay out. */
export function furnitureStoreJsonLd(
	origin: string,
	settings: SiteSettings,
	image: ImageAsset | null
): string {
	const sameAs = [settings.vk_url, ...settings.social_links.map((link) => link.url)].filter(
		(url) => url !== ''
	);
	const address = postalAddress(settings);
	return encode({
		'@context': 'https://schema.org',
		'@type': 'FurnitureStore',
		name: 'Фабрика Уюта',
		url: absoluteUrl(origin, '/'),
		...(settings.phone && { telephone: settings.phone }),
		...(settings.email && { email: settings.email }),
		...(address && { address }),
		...(settings.map_url && { hasMap: settings.map_url }),
		...(sameAs.length > 0 && { sameAs }),
		...(image && { image: absoluteUrl(origin, image.url) })
	});
}

/** The published categories of the home page as a list (tech.md, S2-18). */
export function itemListJsonLd(origin: string, categories: CategorySummary[]): string {
	return encode({
		'@context': 'https://schema.org',
		'@type': 'ItemList',
		itemListElement: categories.map((category, index) => ({
			'@type': 'ListItem',
			position: index + 1,
			name: category.title,
			url: absoluteUrl(origin, `/catalog/${category.slug}`)
		}))
	});
}

/**
 * The path to the current page: the crumb without an href is the page itself.
 * Each step carries the address twice: Google reads `item`, Yandex reads `url`.
 */
export function breadcrumbListJsonLd(origin: string, crumbs: Crumb[]): string {
	return encode({
		'@context': 'https://schema.org',
		'@type': 'BreadcrumbList',
		itemListElement: crumbs.map((crumb, index) => {
			const href = crumb.href ? absoluteUrl(origin, crumb.href) : undefined;
			return {
				'@type': 'ListItem',
				position: index + 1,
				name: crumb.label,
				...(href && { item: href, url: href })
			};
		})
	});
}

/** The whole tag lives here: a literal closing script tag cannot sit inside Svelte markup. */
export function jsonLdScript(json: string): string {
	return `<script type="application/ld+json">${json}</script>`;
}
