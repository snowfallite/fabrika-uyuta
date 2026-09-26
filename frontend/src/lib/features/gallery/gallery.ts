/** Circular step through n photos: from the last forward to the first and back. */
export function nextIndex(index: number, count: number, direction: 1 | -1): number {
	return (((index + direction) % count) + count) % count;
}
