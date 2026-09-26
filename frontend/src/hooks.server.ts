import type { Handle } from '@sveltejs/kit';

// Russian text renders first, so only the Cyrillic faces are preloaded; Latin (digits,
// punctuation) and the rest load on demand without competing with the hero photo.
const CRITICAL_FONT = /(manrope|cormorant-garamond)-cyrillic-wght-normal/;

export const handle: Handle = ({ event, resolve }) =>
	resolve(event, {
		preload: ({ type, path }) =>
			type === 'js' || type === 'css' || (type === 'font' && CRITICAL_FONT.test(path))
	});
