import { createRawSnippet } from 'svelte';
import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import Field from './Field.svelte';

type Args = { id: string; describedBy: string | undefined; invalid: boolean };

const input = createRawSnippet((args: () => Args) => ({
	render: () => {
		const { id, describedBy, invalid } = args();
		const described = describedBy ? ` aria-describedby="${describedBy}"` : '';
		return `<input id="${id}" name="x" aria-invalid="${invalid}"${described} />`;
	}
}));

describe('Field', () => {
	it('links an error to the control: aria-invalid and aria-describedby', async () => {
		const screen = await render(Field, {
			id: 'name',
			label: 'ФИО',
			error: 'Укажите ФИО',
			children: input
		});
		const control = screen.getByLabelText('ФИО');
		await expect.element(control).toHaveAttribute('aria-invalid', 'true');
		await expect.element(control).toHaveAccessibleDescription('Укажите ФИО');
	});

	it('describes the control by hint and error together', async () => {
		const screen = await render(Field, {
			id: 'phone',
			label: 'Телефон',
			hint: 'Перезвоним',
			error: 'Проверьте номер телефона',
			children: input
		});
		await expect
			.element(screen.getByLabelText('Телефон'))
			.toHaveAccessibleDescription('Перезвоним Проверьте номер телефона');
	});

	it('leaves a valid control undescribed', async () => {
		const screen = await render(Field, { id: 'comment', label: 'Комментарий', children: input });
		const control = screen.getByLabelText('Комментарий');
		await expect.element(control).toHaveAttribute('aria-invalid', 'false');
		await expect.element(control).not.toHaveAttribute('aria-describedby');
	});

	it('marks required fields with a hidden asterisk', async () => {
		const screen = await render(Field, {
			id: 'product',
			label: 'Что хотите заказать',
			required: true,
			children: input
		});
		await expect.element(screen.getByLabelText('Что хотите заказать')).toBeInTheDocument();
		await expect.element(screen.getByText('*')).toHaveAttribute('aria-hidden', 'true');
	});
});
