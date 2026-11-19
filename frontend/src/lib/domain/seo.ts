import type { ImageAsset } from '$lib/types';
import { absoluteUrl } from './url';

/** Site cover for pages without a photo of their own (tech.md, appendix A, v16). */
export const OG_FALLBACK = { path: '/og-cover.png', width: 1200, height: 630 };

export type Preview = { url: string; width: number; height: number; alt: string };

/** Link preview of a page: its own photo, otherwise the site cover, so no link travels bare. */
export function previewImage(origin: string, image: ImageAsset | null, title: string): Preview {
	if (image) {
		return {
			url: absoluteUrl(origin, image.url),
			width: image.width,
			height: image.height,
			alt: image.alt
		};
	}
	return {
		url: absoluteUrl(origin, OG_FALLBACK.path),
		width: OG_FALLBACK.width,
		height: OG_FALLBACK.height,
		alt: title
	};
}
