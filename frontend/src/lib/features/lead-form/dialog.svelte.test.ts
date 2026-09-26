import { describe, expect, it } from 'vitest';
import { leadDialog, openFromLink } from './dialog.svelte';

const click = (init: MouseEventInit = {}) =>
	new MouseEvent('click', { button: 0, cancelable: true, ...init });

describe('lead dialog state', () => {
	it('opens without a kind and closes', () => {
		leadDialog.open();
		expect(leadDialog.isOpen).toBe(true);
		expect(leadDialog.product).toBe('');
		leadDialog.close();
		expect(leadDialog.isOpen).toBe(false);
	});

	it('AC4: open(product) remembers the kind for the form', () => {
		leadDialog.open('wardrobes');
		expect(leadDialog.product).toBe('wardrobes');
		leadDialog.open();
		expect(leadDialog.product).toBe('');
		leadDialog.close();
	});

	it('a plain click opens the dialog instead of following the link', () => {
		const event = click();
		openFromLink(event, 'office');
		expect(event.defaultPrevented).toBe(true);
		expect(leadDialog.isOpen).toBe(true);
		expect(leadDialog.product).toBe('office');
		leadDialog.close();
	});

	it('modifier clicks keep the link behaviour', () => {
		for (const init of [{ ctrlKey: true }, { metaKey: true }, { shiftKey: true }, { button: 1 }]) {
			const event = click(init);
			openFromLink(event);
			expect(event.defaultPrevented).toBe(false);
			expect(leadDialog.isOpen).toBe(false);
		}
	});
});
