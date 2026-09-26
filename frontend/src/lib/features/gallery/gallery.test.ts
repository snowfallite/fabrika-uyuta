import { describe, expect, it } from 'vitest';
import fc from 'fast-check';
import { nextIndex } from './gallery';

const numRuns = process.env.CI ? 200 : 50;
const position = fc
	.integer({ min: 1, max: 50 })
	.chain((count) => fc.tuple(fc.integer({ min: 0, max: count - 1 }), fc.constant(count)));

describe('nextIndex', () => {
	it('wraps around both ends', () => {
		expect(nextIndex(4, 5, 1)).toBe(0);
		expect(nextIndex(0, 5, -1)).toBe(4);
		expect(nextIndex(2, 5, 1)).toBe(3);
	});

	it('always stays in range', () => {
		fc.assert(
			fc.property(position, fc.constantFrom<1 | -1>(1, -1), ([index, count], direction) => {
				const next = nextIndex(index, count, direction);
				expect(next).toBeGreaterThanOrEqual(0);
				expect(next).toBeLessThan(count);
			}),
			{ numRuns }
		);
	});

	it('forward then back returns to the start, n steps make a full circle', () => {
		fc.assert(
			fc.property(position, ([index, count]) => {
				expect(nextIndex(nextIndex(index, count, 1), count, -1)).toBe(index);
				let current = index;
				for (let step = 0; step < count; step += 1) current = nextIndex(current, count, 1);
				expect(current).toBe(index);
			}),
			{ numRuns }
		);
	});
});
