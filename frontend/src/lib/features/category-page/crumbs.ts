import { CATEGORY_PAGE } from '$lib/content/pages';
import type { Crumb } from '$lib/domain/json-ld';

/** Path of a category page: home, the catalog anchor, then the page itself (tech.md, S2-18). */
export function categoryCrumbs(title: string): Crumb[] {
	return [
		{ label: CATEGORY_PAGE.crumbHome, href: '/' },
		{ label: CATEGORY_PAGE.crumbCatalog, href: '/#catalog' },
		{ label: title }
	];
}
