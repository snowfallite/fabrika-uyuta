import { describe, expect, it } from 'vitest';
import fc from 'fast-check';
import { splitParagraphs } from './text';

const numRuns = process.env.CI ? 200 : 50;
const squash = (value: string) => value.replace(/\s/g, '');

describe('splitParagraphs', () => {
	it('splits on blank lines and trims', () => {
		expect(splitParagraphs('Первый.\n\n  Второй  \n \n\nТретий\nс переносом')).toEqual([
			'Первый.',
			'Второй',
			'Третий\nс переносом'
		]);
		expect(splitParagraphs('   ')).toEqual([]);
	});

	it('never returns empty paragraphs and keeps every non-space character', () => {
		fc.assert(
			fc.property(fc.string({ unit: fc.constantFrom('a', 'б', ' ', '\n', '\t', '.') }), (text) => {
				const paragraphs = splitParagraphs(text);
				for (const paragraph of paragraphs) expect(paragraph.trim()).not.toBe('');
				expect(squash(paragraphs.join(''))).toBe(squash(text));
			}),
			{ numRuns }
		);
	});
});
