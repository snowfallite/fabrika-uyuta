/** Category description -> paragraphs: split on blank lines, trim, drop empty ones. */
export function splitParagraphs(text: string): string[] {
	return text
		.split(/\n\s*\n/)
		.map((paragraph) => paragraph.trim())
		.filter(Boolean);
}
