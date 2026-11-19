import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import type { ProductOption } from '$lib/types';
import LeadForm from './LeadForm.svelte';

const OPTIONS: ProductOption[] = [
	{ value: 'kitchens', label: 'Кухни под заказ' },
	{ value: 'kids-rooms', label: 'Детские комнаты' }
];

function props(extra: Record<string, unknown> = {}) {
	return {
		idPrefix: 'test',
		options: OPTIONS,
		phone: '+79990000001',
		phoneDisplay: '+7 (999) 000-00-01',
		...extra
	};
}

function kindSelect(container: HTMLElement): HTMLSelectElement {
	const select = container.querySelector<HTMLSelectElement>('select[name="product"]');
	if (select === null) throw new Error('the kind select is missing');
	return select;
}

describe('LeadForm', () => {
	it('AC2: the kind list holds the categories the API sent, in their order', async () => {
		const screen = await render(LeadForm, props());

		const entries = [...kindSelect(screen.container).options].map((option) => [
			option.value,
			option.textContent
		]);

		expect(entries).toEqual([
			['', 'Выберите'],
			['kitchens', 'Кухни под заказ'],
			['kids-rooms', 'Детские комнаты']
		]);
	});

	it('AC8: a kind from the list starts selected', async () => {
		const screen = await render(LeadForm, props({ product: 'kids-rooms' }));

		expect(kindSelect(screen.container).value).toBe('kids-rooms');
	});

	it('AC8: a kind the list does not offer leaves the placeholder', async () => {
		const screen = await render(LeadForm, props({ product: 'spaceship' }));

		expect(kindSelect(screen.container).value).toBe('');
	});

	it('AC9: without published categories only the placeholder is left', async () => {
		const screen = await render(LeadForm, props({ options: [], product: 'kitchens' }));

		const select = kindSelect(screen.container);
		expect([...select.options].map((option) => option.value)).toEqual(['']);
		expect(select.value).toBe('');
	});
});
