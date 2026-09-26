import type { ImageAsset, SiteSettings } from '$lib/types';
import { absoluteUrl } from './url';

/** FurnitureStore structured data for the home page (tech.md, S2-11); empty fields stay out. */
export function furnitureStoreJsonLd(
	origin: string,
	settings: SiteSettings,
	image: ImageAsset | null
): string {
	const data = {
		'@context': 'https://schema.org',
		'@type': 'FurnitureStore',
		name: 'Фабрика Уюта',
		url: absoluteUrl(origin, '/'),
		...(settings.phone && { telephone: settings.phone }),
		...(settings.address && { address: settings.address }),
		...(image && { image: absoluteUrl(origin, image.url) })
	};
	// "<" escaped: the JSON sits inside a <script> element.
	return JSON.stringify(data).replace(/</g, '\\u003c');
}

/** The whole tag lives here: a literal closing script tag cannot sit inside Svelte markup. */
export function jsonLdScript(json: string): string {
	return `<script type="application/ld+json">${json}</script>`;
}
