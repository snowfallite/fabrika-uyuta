import { createRawSnippet } from 'svelte';
import { describe, expect, it, vi } from 'vitest';
import { render } from 'vitest-browser-svelte';
import Button from './button.svelte';

const label = (text: string) => createRawSnippet(() => ({ render: () => `<span>${text}</span>` }));

describe('Button', () => {
	it('blocks clicks while loading and reports aria-busy', async () => {
		const onclick = vi.fn();
		const screen = await render(Button, {
			loading: true,
			onclick,
			children: label('Отправляем…')
		});
		const button = screen.getByRole('button', { name: 'Отправляем…' });
		await expect.element(button).toBeDisabled();
		await expect.element(button).toHaveAttribute('aria-busy', 'true');
		(button.element() as HTMLButtonElement).click();
		expect(onclick).not.toHaveBeenCalled();
	});

	it('clicks when idle', async () => {
		const onclick = vi.fn();
		const screen = await render(Button, { onclick, children: label('Отправить заявку') });
		await screen.getByRole('button', { name: 'Отправить заявку' }).click();
		expect(onclick).toHaveBeenCalledOnce();
	});

	it('renders a link when href is set', async () => {
		const screen = await render(Button, { href: '/lead', children: label('Оставить заявку') });
		await expect
			.element(screen.getByRole('link', { name: 'Оставить заявку' }))
			.toHaveAttribute('href', '/lead');
	});
});
