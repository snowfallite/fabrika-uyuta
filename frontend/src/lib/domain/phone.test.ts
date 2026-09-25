import { describe, expect, it } from 'vitest';
import fc from 'fast-check';
import cases from '../../../../contracts/fixtures/phone-cases.json';
import { formatPhoneInput } from './phone';

const numRuns = process.env.CI ? 200 : 50;

describe('formatPhoneInput', () => {
	it.each(cases)('AC6: masks $input as $masked', ({ input, masked }) => {
		expect(formatPhoneInput(input)).toBe(masked);
	});

	it('is idempotent', () => {
		fc.assert(
			fc.property(fc.string(), (raw) => {
				const once = formatPhoneInput(raw);
				expect(formatPhoneInput(once)).toBe(once);
			}),
			{ numRuns }
		);
	});

	it('outputs only digits, plus, spaces, brackets and dashes', () => {
		fc.assert(
			fc.property(fc.string(), (raw) => {
				expect(formatPhoneInput(raw)).toMatch(/^[\d+ ()-]*$/);
			}),
			{ numRuns }
		);
	});

	it('keeps at most 11 digits for +7 numbers', () => {
		fc.assert(
			fc.property(fc.stringMatching(/^[\d ()+-]{0,40}$/), (raw) => {
				const masked = formatPhoneInput(raw);
				if (masked.startsWith('+7')) {
					expect(masked.replace(/\D/g, '').length).toBeLessThanOrEqual(11);
				}
			}),
			{ numRuns }
		);
	});

	it('never throws', () => {
		fc.assert(
			fc.property(fc.string({ unit: 'binary' }), (raw) => {
				expect(() => formatPhoneInput(raw)).not.toThrow();
			}),
			{ numRuns }
		);
	});
});
