import AxeBuilder from '@axe-core/playwright';
import { expect, type Page } from '@playwright/test';

/** Fails on serious and critical axe violations (tech.md, section 1). */
export async function expectNoSeriousA11yViolations(page: Page) {
	const { violations } = await new AxeBuilder({ page }).analyze();
	const blocking = violations
		.filter((v) => v.impact === 'serious' || v.impact === 'critical')
		.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(' ')).join(', ')}`);
	expect(blocking).toEqual([]);
}
