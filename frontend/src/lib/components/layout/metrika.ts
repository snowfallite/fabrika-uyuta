type YmQueue = ((...args: unknown[]) => void) & { a?: unknown[][]; l?: number };
type WindowWithYm = Window & typeof globalThis & { ym?: YmQueue };

const TAG_SRC = 'https://mc.yandex.ru/metrika/tag.js';

/**
 * The official Yandex.Metrika snippet rewritten as module code: the tag is created here,
 * so the page carries no inline script and CSP needs no nonce (tech.md, 10.2).
 * Returns the cleanup that removes the tag again.
 */
export function startMetrika(id: number): () => void {
	const target = window as WindowWithYm;
	if (!target.ym) {
		const queue: YmQueue = (...args: unknown[]) => {
			queue.a = queue.a ?? [];
			queue.a.push(args);
		};
		queue.l = Date.now();
		target.ym = queue;
	}
	target.ym(id, 'init', { clickmap: true, trackLinks: true, accurateTrackBounce: true });
	const script = document.createElement('script');
	script.src = TAG_SRC;
	script.async = true;
	document.head.append(script);
	return () => script.remove();
}
