import type { ProductKind } from '$lib/types';

// A new kind in OpenAPI without a label here breaks svelte-check (tech.md, 10.4).
export const PRODUCT_KIND_LABELS = {
	kitchens: 'Кухни под заказ',
	'kitchen-tables': 'Кухонные столы',
	wardrobes: 'Шкафы',
	'sliding-wardrobes': 'Шкафы-купе',
	office: 'Офисная мебель',
	other: 'Другое'
} satisfies Record<ProductKind, string>;

export function isProductKind(value: unknown): value is ProductKind {
	return typeof value === 'string' && Object.hasOwn(PRODUCT_KIND_LABELS, value);
}
