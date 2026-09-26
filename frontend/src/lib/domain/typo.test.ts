import fc from 'fast-check';
import { describe, expect, it } from 'vitest';
import { nbsp, typo } from './typo';

const NBSP = String.fromCharCode(160);

describe('nbsp', () => {
	it('binds short words to the next word', () => {
		expect(nbsp('Мебель на заказ в Вологде')).toBe(`Мебель на${NBSP}заказ в${NBSP}Вологде`);
		expect(nbsp('Надёжные механизмы и аккуратные детали.')).toBe(
			`Надёжные механизмы и${NBSP}аккуратные детали.`
		);
	});

	it('handles a chain of short words and a leading one', () => {
		expect(nbsp('и в дом')).toBe(`и${NBSP}в${NBSP}дом`);
	});

	it('leaves longer words, numbers and punctuation alone', () => {
		expect(nbsp('Стена 3,2 м, высота 2,6 м')).toBe('Стена 3,2 м, высота 2,6 м');
		expect(nbsp('Кухни, шкафы, столы')).toBe('Кухни, шкафы, столы');
	});

	it('only swaps spaces: text without spaces is unchanged, length is kept', () => {
		fc.assert(
			fc.property(fc.string(), (text) => {
				const out = nbsp(text);
				expect(out.length).toBe(text.length);
				expect(out.replaceAll(NBSP, ' ')).toBe(text.replaceAll(NBSP, ' '));
				expect(nbsp(out)).toBe(out);
			})
		);
	});
});

describe('typo', () => {
	it('keeps the shape and maps nested strings', () => {
		const out = typo({
			title: 'Путь от заявки до готовой мебели',
			steps: [{ text: 'и в срок' }],
			n: 1
		});
		expect(out).toEqual({
			title: `Путь от${NBSP}заявки до${NBSP}готовой мебели`,
			steps: [{ text: `и${NBSP}в${NBSP}срок` }],
			n: 1
		});
	});
});
