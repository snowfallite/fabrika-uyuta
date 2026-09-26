export { cn } from 'cn';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type WithoutChild<T> = T extends { child?: any } ? Omit<T, 'child'> : T;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type WithoutChildren<T> = T extends { children?: any } ? Omit<T, 'children'> : T;
export type WithoutChildrenOrChild<T> = WithoutChildren<WithoutChild<T>>;
export type WithElementRef<T, U extends HTMLElement = HTMLElement> = T & { ref?: U | null };

/** Template reveal-on-scroll; the hidden state exists only once JS runs. */
export function reveal(node: HTMLElement, delay = 0) {
	if (!('IntersectionObserver' in window)) return;
	node.classList.add('reveal');
	node.style.transitionDelay = `${delay}ms`;
	const observer = new IntersectionObserver(
		([entry]) => {
			if (entry?.isIntersecting) {
				node.classList.add('is-visible');
				observer.disconnect();
				// The stagger delay is for the entrance only; hover transitions must not wait for it.
				node.addEventListener('transitionend', () => (node.style.transitionDelay = ''), {
					once: true
				});
			}
		},
		{ threshold: 0.12 }
	);
	observer.observe(node);
	return { destroy: () => observer.disconnect() };
}
