import { describe, expect, it, vi } from 'vitest';

const env = vi.hoisted(() => ({ PUBLIC_APP_ENV: 'dev' }));
vi.mock('$env/dynamic/public', () => ({ env }));

const { load } = await import('./+page.server');
type LoadEvent = Parameters<typeof load>[0];

describe('/dev/ui load', () => {
	it('AC3: answers 404 in production', () => {
		env.PUBLIC_APP_ENV = 'production';
		expect(() => load({} as LoadEvent)).toThrow(expect.objectContaining({ status: 404 }));
	});

	it('AC3: opens in other environments', () => {
		env.PUBLIC_APP_ENV = 'staging';
		expect(() => load({} as LoadEvent)).not.toThrow();
	});
});
