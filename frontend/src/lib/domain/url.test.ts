import { describe, expect, it } from 'vitest';
import fc from 'fast-check';
import { absoluteUrl } from './url';

const numRuns = process.env.CI ? 200 : 50;
const origin = fc.constantFrom(
	'https://example.com',
	'https://example.com/',
	'http://localhost:8080'
);
const segment = fc.stringMatching(/^[a-z0-9-]{0,8}$/);
const path = fc.array(segment, { maxLength: 5 }).map((parts) => '/' + parts.join('/'));

describe('absoluteUrl', () => {
	it('joins origin and path with one slash', () => {
		expect(absoluteUrl('https://example.com/', '/catalog/kitchens')).toBe(
			'https://example.com/catalog/kitchens'
		);
		expect(absoluteUrl('https://example.com', 'media/a.webp')).toBe(
			'https://example.com/media/a.webp'
		);
	});

	it('starts with the origin and has no double slashes after the scheme', () => {
		fc.assert(
			fc.property(origin, path, fc.boolean(), (base, tail, doubled) => {
				const url = absoluteUrl(base, doubled ? tail.replace('/', '//') : tail);
				expect(url.startsWith(base.replace(/\/$/, ''))).toBe(true);
				expect(url.replace(/^https?:\/\//, '')).not.toContain('//');
			}),
			{ numRuns }
		);
	});
});
