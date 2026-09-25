import { expect, test } from '@playwright/test';
import { expectNoSeriousA11yViolations } from './axe';

// Runs on seed_demo data: every slot has a photo.
test.describe('home: hero', () => {
	test('AC1: the hero photo renders with srcset of all variants and its size', async ({ page }) => {
		await page.goto('/');
		const hero = page.locator('#hero img');
		const srcset = (await hero.getAttribute('srcset')) ?? '';
		const widths = [...srcset.matchAll(/ (\d+)w/g)].map((m) => Number(m[1]));
		expect(widths.length).toBeGreaterThan(1);
		expect(widths).toEqual([...widths].sort((a, b) => a - b));
		await expect(hero).toHaveAttribute('width', String(widths.at(-1)));
		await expect(hero).toHaveAttribute('height', /^\d+$/);
		await expect(page.getByRole('heading', { level: 1 })).toHaveText('Мебель на заказ в Вологде');
	});

	test('AC3: the hero photo is the LCP element and is not lazy', async ({ page }) => {
		await page.goto('/', { waitUntil: 'load' });
		const hero = page.locator('#hero img');
		await expect(hero).toHaveAttribute('loading', 'eager');
		await expect(hero).toHaveAttribute('fetchpriority', 'high');
		const lcp = await page.evaluate(
			() =>
				new Promise<string>((resolve) => {
					new PerformanceObserver((list) => {
						const entries = list.getEntries() as (PerformanceEntry & { element?: Element })[];
						const last = entries.at(-1);
						resolve(
							last?.element?.closest('#hero') && last.element.tagName === 'IMG' ? 'hero' : 'other'
						);
					}).observe({ type: 'largest-contentful-paint', buffered: true });
				})
		);
		expect(lcp).toBe('hero');
	});

	test('home has no serious axe issues', async ({ page }) => {
		await page.goto('/', { waitUntil: 'networkidle' });
		await expectNoSeriousA11yViolations(page);
	});
});
