<script lang="ts">
	import { enhance } from '$app/forms';
	import { page } from '$app/state';
	import type { SubmitFunction } from '@sveltejs/kit';
	import { tick, untrack } from 'svelte';
	import { Alert } from '$lib/components/ui/alert';
	import { Button } from '$lib/components/ui/button';
	import { Checkbox } from '$lib/components/ui/checkbox';
	import { Field } from '$lib/components/ui/field';
	import { Input } from '$lib/components/ui/input';
	import { PhoneInput } from '$lib/components/ui/phone-input';
	import { Select } from '$lib/components/ui/select';
	import { Textarea } from '$lib/components/ui/textarea';
	import { LEAD_FIELDS, LEAD_MESSAGES } from '$lib/content/lead-form';
	import type { LeadFormErrors } from '$lib/domain/lead-errors';
	import type { ProductOption } from '$lib/types';
	import { EMPTY_VALUES, firstInvalid, type LeadFailure, type LeadResult } from './lead-form';
	import LeadSuccess from './LeadSuccess.svelte';

	interface Props {
		/** Keeps ids unique when the page and the dialog both hold a form. */
		idPrefix: string;
		/** Kind list from the API: published categories by position (tech.md, 12.1). */
		options: ProductOption[];
		product?: string;
		/** Company phone for the error alerts, E.164 and display form. */
		phone: string;
		phoneDisplay: string;
		/** Server result for the no-JS render of /lead. */
		result?: LeadResult | null;
	}

	let { idPrefix, options, product = '', phone, phoneDisplay, result = null }: Props = $props();

	type Status = 'idle' | 'submitting' | 'success' | 'throttled' | 'unavailable';

	const failure = (value: LeadResult | null) =>
		value && !('success' in value) ? (value as LeadFailure) : null;

	// The form owns its state after mount; props only seed it. A kind the list does not offer
	// (an old link, a category taken off the site) leaves the placeholder in place.
	const seed = untrack(() => ({
		result,
		product: options.some((option) => option.value === product) ? product : ''
	}));
	const initial = failure(seed.result);
	let values = $state(initial ? { ...initial.values } : { ...EMPTY_VALUES, product: seed.product });
	let errors = $state<LeadFormErrors>(initial?.errors ?? {});
	let status = $state<Status>(
		seed.result && 'success' in seed.result ? 'success' : (initial?.status ?? 'idle')
	);
	// Without JS only the autofocus attribute can move focus to the first bad field.
	const autofocusField = firstInvalid(initial?.errors ?? {});

	const sourceUrl = $derived((page.url.pathname + page.url.search).slice(0, 2000));
	const id = (name: string) => `${idPrefix}-${name}`;

	const submit: SubmitFunction = ({ cancel }) => {
		if (status === 'submitting') {
			cancel();
			return;
		}
		status = 'submitting';
		return async ({ result: outcome, formElement }) => {
			if (outcome.type === 'success') {
				values = { ...EMPTY_VALUES, product: seed.product };
				errors = {};
				status = 'success';
				return;
			}
			const data = outcome.type === 'failure' ? failure(outcome.data as LeadResult) : null;
			errors = data?.errors ?? {};
			status = data?.status ?? (data ? 'idle' : 'unavailable');
			const field = firstInvalid(errors);
			if (field) {
				await tick();
				formElement.querySelector<HTMLElement>(`#${id(field)}`)?.focus();
			}
		};
	};

	// A field's error goes away as soon as the visitor edits that field.
	function clearError(event: Event) {
		const name = (event.target as HTMLInputElement | null)?.name;
		if (name && name in errors) errors = { ...errors, [name]: undefined };
	}

	function again() {
		status = 'idle';
		errors = {};
	}
</script>

{#if status === 'success'}
	<LeadSuccess onagain={again} />
{:else}
	<form
		method="POST"
		action="/lead"
		novalidate
		use:enhance={submit}
		oninput={clearError}
		onchange={clearError}
		class="@container/lead space-y-6"
	>
		<!-- A wide form (the dialog) pairs the short fields; a narrow one keeps one column. -->
		<div class="grid gap-6 @xl/lead:grid-cols-2 @xl/lead:gap-x-8">
			<Field id={id('name')} label={LEAD_FIELDS.name.label} required error={errors.name}>
				{#snippet children({ id, describedBy, invalid })}
					<Input
						{id}
						name="name"
						bind:value={values.name}
						required
						maxlength={120}
						autocomplete="name"
						placeholder={LEAD_FIELDS.name.placeholder}
						aria-invalid={invalid}
						aria-describedby={describedBy}
						autofocus={autofocusField === 'name'}
					/>
				{/snippet}
			</Field>
			<Field id={id('phone')} label={LEAD_FIELDS.phone.label} required error={errors.phone}>
				{#snippet children({ id, describedBy, invalid })}
					<PhoneInput
						{id}
						name="phone"
						bind:value={values.phone}
						required
						aria-invalid={invalid}
						aria-describedby={describedBy}
						autofocus={autofocusField === 'phone'}
					/>
				{/snippet}
			</Field>
			<Field id={id('product')} label={LEAD_FIELDS.product.label} required error={errors.product}>
				{#snippet children({ id, describedBy, invalid })}
					<Select
						{id}
						name="product"
						{options}
						bind:value={values.product}
						placeholder={LEAD_FIELDS.product.placeholder}
						required
						aria-invalid={invalid}
						aria-describedby={describedBy}
						autofocus={autofocusField === 'product'}
					/>
				{/snippet}
			</Field>
			<Field id={id('dimensions')} label={LEAD_FIELDS.dimensions.label} error={errors.dimensions}>
				{#snippet children({ id, describedBy, invalid })}
					<Input
						{id}
						name="dimensions"
						bind:value={values.dimensions}
						maxlength={300}
						placeholder={LEAD_FIELDS.dimensions.placeholder}
						aria-invalid={invalid}
						aria-describedby={describedBy}
						autofocus={autofocusField === 'dimensions'}
					/>
				{/snippet}
			</Field>
		</div>

		<Field id={id('comment')} label={LEAD_FIELDS.comment.label} error={errors.comment}>
			{#snippet children({ id, describedBy, invalid })}
				<Textarea
					{id}
					name="comment"
					bind:value={values.comment}
					maxlength={2000}
					placeholder={LEAD_FIELDS.comment.placeholder}
					aria-invalid={invalid}
					aria-describedby={describedBy}
					autofocus={autofocusField === 'comment'}
				/>
			{/snippet}
		</Field>
		<!-- Honeypot: people never see it, bots fill it (tech.md, 12.1). -->
		<div aria-hidden="true" class="absolute -left-[9999px] h-px w-px overflow-hidden">
			<label for={id('website')}>Сайт</label>
			<input id={id('website')} name="website" type="text" tabindex="-1" autocomplete="off" />
		</div>
		<input type="hidden" name="source_url" value={sourceUrl} />

		{#if status === 'throttled' || status === 'unavailable'}
			<Alert tone="error">
				{status === 'throttled' ? LEAD_MESSAGES.throttled : LEAD_MESSAGES.unavailable}
				{#if phone}
					<a href="tel:{phone}" class="font-medium whitespace-nowrap underline">{phoneDisplay}</a>
				{/if}
			</Alert>
		{:else if errors.form}
			<Alert tone="error">{errors.form}</Alert>
		{/if}

		<!-- Consent stands beside the button on a wide form and above it on a narrow one. -->
		<div
			class="flex flex-col gap-6 @xl/lead:flex-row @xl/lead:items-center @xl/lead:justify-between @xl/lead:gap-10"
		>
			<Field id={id('consent')} label="" error={errors.consent}>
				{#snippet children({ id, describedBy, invalid })}
					<Checkbox
						{id}
						name="consent"
						bind:checked={values.consent}
						required
						aria-invalid={invalid}
						aria-describedby={describedBy}
						autofocus={autofocusField === 'consent'}
					>
						{LEAD_FIELDS.consent.before}<a
							href="/consent"
							class="text-primary underline underline-offset-2">{LEAD_FIELDS.consent.link}</a
						>
					</Checkbox>
				{/snippet}
			</Field>
			<Button type="submit" class="w-full @xl/lead:w-auto" loading={status === 'submitting'}>
				{status === 'submitting' ? LEAD_MESSAGES.sending : LEAD_MESSAGES.submit}
			</Button>
		</div>
	</form>
{/if}
