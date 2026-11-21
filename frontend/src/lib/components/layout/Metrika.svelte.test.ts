import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render } from 'vitest-browser-svelte';
import Metrika from './Metrika.svelte';

// The real loader would fetch mc.yandex.ru, and unit tests take no network (tech.md, 17).
const startMetrika = vi.hoisted(() => vi.fn(() => () => undefined));
vi.mock('./metrika', () => ({ startMetrika }));

describe('Metrika', () => {
	beforeEach(() => {
		startMetrika.mockClear();
	});

	it('AC7: an empty counter id loads nothing', async () => {
		const screen = await render(Metrika, { id: '' });
		expect(startMetrika).not.toHaveBeenCalled();
		expect(screen.container.innerHTML).not.toContain('yandex');
	});

	it('AC7: a counter id starts the tag with that number', async () => {
		await render(Metrika, { id: '12345678' });
		expect(startMetrika).toHaveBeenCalledWith(12345678);
	});

	it('AC7: a non-numeric id loads nothing', async () => {
		await render(Metrika, { id: 'not-a-number' });
		expect(startMetrika).not.toHaveBeenCalled();
	});
});
