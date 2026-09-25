import type { LeadFormErrors } from '$lib/domain/lead-errors';

/** Values the form sends back on failure; honeypot and source stay out. */
export type LeadValues = {
	name: string;
	phone: string;
	product: string;
	dimensions: string;
	comment: string;
	consent: boolean;
};

export type LeadFailure = {
	values: LeadValues;
	errors: LeadFormErrors;
	status?: 'throttled' | 'unavailable';
};

export type LeadResult = { success: true } | LeadFailure;

/** Form order: the first of these with an error takes focus. */
const FIELD_ORDER = ['name', 'phone', 'product', 'dimensions', 'comment', 'consent'] as const;

export function firstInvalid(errors: LeadFormErrors) {
	return FIELD_ORDER.find((field) => errors[field]);
}

export const EMPTY_VALUES: LeadValues = {
	name: '',
	phone: '',
	product: '',
	dimensions: '',
	comment: '',
	consent: false
};

const text = (data: FormData, key: string) => {
	const value = data.get(key);
	return typeof value === 'string' ? value : '';
};

export function readLeadForm(data: FormData) {
	return {
		values: {
			name: text(data, 'name'),
			phone: text(data, 'phone'),
			product: text(data, 'product'),
			dimensions: text(data, 'dimensions'),
			comment: text(data, 'comment'),
			consent: data.get('consent') === 'on'
		} satisfies LeadValues,
		website: text(data, 'website'),
		sourceUrl: text(data, 'source_url').slice(0, 2000)
	};
}
