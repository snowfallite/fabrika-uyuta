import { describe, expect, it } from 'vitest';
import fc from 'fast-check';
import { absoluteUrl, sitePath } from './url';

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

const hostile = fc.constantFrom(
	'//evil.test/x',
	'/\\evil.test/x',
	'/..//evil.test',
	'https://evil.test/x',
	'http:/evil.test',
	'javascript:alert(1)',
	'/lead?product=office#anchor',
	'/'
);

describe('sitePath', () => {
	it('keeps a path of this site and drops anything else', () => {
		expect(sitePath('/catalog/kitchens?product=office')).toBe('/catalog/kitchens?product=office');
		expect(sitePath('//evil.test/x')).toBe('/');
		expect(sitePath('/..//evil.test')).toBe('/');
		expect(sitePath('https://evil.test/x')).toBe('/');
		expect(sitePath(null)).toBe('/');
		expect(sitePath('')).toBe('/');
	});

	it('AC6: always returns a path of this site and never throws', () => {
		fc.assert(
			fc.property(fc.oneof(fc.string(), fc.webUrl(), path, hostile), (raw) => {
				const result = sitePath(raw);
				expect(result.startsWith('/')).toBe(true);
				expect(result.startsWith('//')).toBe(false);
				expect(result.startsWith('/\\')).toBe(false);
			}),
			{ numRuns }
		);
	});
});
