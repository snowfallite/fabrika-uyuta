const FIELDS = ['name', 'phone', 'product', 'dimensions', 'comment', 'consent'] as const;
type LeadField = (typeof FIELDS)[number];

export type LeadFormErrors = Partial<Record<LeadField | 'form', string>>;

const isField = (key: string): key is LeadField => (FIELDS as readonly string[]).includes(key);

function firstMessage(value: unknown): string | undefined {
	const candidate = Array.isArray(value) ? value[0] : value;
	return typeof candidate === 'string' && candidate ? candidate : undefined;
}

/** DRF 400 body -> one message per form field; unknown keys land in `form` (tech.md, 10.4). */
export function mapLeadErrors(body: unknown): LeadFormErrors {
	const errors: LeadFormErrors = {};
	if (!body || typeof body !== 'object' || Array.isArray(body)) return errors;
	for (const [key, value] of Object.entries(body)) {
		const message = firstMessage(value);
		const target = isField(key) ? key : 'form';
		if (message && !errors[target]) errors[target] = message;
	}
	return errors;
}
