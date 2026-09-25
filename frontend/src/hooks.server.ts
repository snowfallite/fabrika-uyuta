import type { Handle } from '@sveltejs/kit';

// Latin and Cyrillic faces render every page; the other subsets load on demand.
const CRITICAL_FONT = /(manrope|cormorant-garamond)-(latin|cyrillic)-wght-normal/;

export const handle: Handle = ({ event, resolve }) =>
	resolve(event, {
		preload: ({ type, path }) =>
			type === 'js' || type === 'css' || (type === 'font' && CRITICAL_FONT.test(path))
	});
