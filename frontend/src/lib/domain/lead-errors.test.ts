import { describe, expect, it } from 'vitest';
import fc from 'fast-check';
import { mapLeadErrors } from './lead-errors';

const numRuns = process.env.CI ? 200 : 50;
const KEYS = ['name', 'phone', 'product', 'dimensions', 'comment', 'consent', 'form'];

describe('mapLeadErrors', () => {
	it('maps DRF field errors to the first message of each field', () => {
		expect(
			mapLeadErrors({
				name: ['Укажите ФИО', 'второе'],
				phone: ['Проверьте номер телефона'],
				consent: ['Нужно согласие на обработку персональных данных']
			})
		).toEqual({
			name: 'Укажите ФИО',
			phone: 'Проверьте номер телефона',
			consent: 'Нужно согласие на обработку персональных данных'
		});
	});

	it('sends unknown keys and non_field_errors to form', () => {
		expect(mapLeadErrors({ non_field_errors: ['Ошибка'], detail: 'x' })).toEqual({
			form: 'Ошибка'
		});
		expect(mapLeadErrors({ source_url: ['Слишком длинно'] })).toEqual({ form: 'Слишком длинно' });
	});

	it('returns nothing for bodies that are not objects', () => {
		for (const body of [null, undefined, 'text', 42, ['name']]) {
			expect(mapLeadErrors(body)).toEqual({});
		}
	});

	it('any body yields only known keys with non-empty string messages', () => {
		fc.assert(
			fc.property(fc.anything(), (body) => {
				const errors = mapLeadErrors(body);
				for (const [key, value] of Object.entries(errors)) {
					expect(KEYS).toContain(key);
					expect(typeof value).toBe('string');
					expect(value).not.toBe('');
				}
			}),
			{ numRuns }
		);
	});

	it('DRF-shaped bodies keep every known field message', () => {
		const drfBody = fc.dictionary(
			fc.constantFrom(...KEYS.filter((k) => k !== 'form')),
			fc.array(fc.string({ minLength: 1 }), { minLength: 1 })
		);
		fc.assert(
			fc.property(drfBody, (body) => {
				const errors = mapLeadErrors(body);
				for (const [key, messages] of Object.entries(body)) {
					expect(errors[key as keyof typeof errors]).toBe(messages[0]);
				}
			}),
			{ numRuns }
		);
	});
});
