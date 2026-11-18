/**
 * Desktop grid tracks taken by a card. A row holds six tracks, and the count of
 * categories is free since v14, so the leftover cards of the first row widen to
 * fill it (tech.md, S2-16 AC7).
 */
export function cardSpan(index: number, count: number): 2 | 3 | 6 {
	const leftover = count % 3;
	if (leftover === 2 && index < 2) return 3;
	if (leftover === 1 && index === 0) return 6;
	return 2;
}
