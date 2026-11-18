import fc from 'fast-check';
import { describe, expect, it } from 'vitest';
import { cardSpan } from './categories';

const ROW = 6;

describe('cardSpan', () => {
	it('AC7: any number of cards fills its rows without a hole', () => {
		fc.assert(
			fc.property(fc.integer({ min: 1, max: 60 }), (count) => {
				let row = 0;
				for (let index = 0; index < count; index += 1) {
					row += cardSpan(index, count);
					expect(row).toBeLessThanOrEqual(ROW);
					if (row === ROW) row = 0;
				}
				expect(row).toBe(0);
			}),
			{ numRuns: process.env.CI ? 200 : 50 }
		);
	});

	it('AC7: a card never takes less than a third or more than a whole row', () => {
		fc.assert(
			fc.property(fc.integer({ min: 1, max: 60 }), (count) => {
				for (let index = 0; index < count; index += 1) {
					expect([2, 3, ROW]).toContain(cardSpan(index, count));
				}
			}),
			{ numRuns: process.env.CI ? 200 : 50 }
		);
	});

	it('AC7: five categories keep the template layout, two wide over three narrow', () => {
		expect([0, 1, 2, 3, 4].map((index) => cardSpan(index, 5))).toEqual([3, 3, 2, 2, 2]);
	});
});
