// Russian typography: a one- or two-letter word (preposition, conjunction) never ends a line.
const NBSP = String.fromCharCode(160);
const SHORT_WORD = new RegExp(`(?<=^|[\\s${NBSP}(«])([а-яёa-z]{1,2}) `, 'giu');

export function nbsp(text: string): string {
	return text.replace(SHORT_WORD, `$1${NBSP}`);
}

/** Applies nbsp to every string of a static text object; keys and shape stay the same. */
export function typo<T>(value: T): T {
	if (typeof value === 'string') return nbsp(value) as T;
	if (Array.isArray(value)) return value.map((item) => typo(item)) as T;
	if (value && typeof value === 'object') {
		return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, typo(item)])) as T;
	}
	return value;
}
