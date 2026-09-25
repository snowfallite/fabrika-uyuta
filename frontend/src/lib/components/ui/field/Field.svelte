<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		id: string;
		/** Empty string renders no <label>: a Checkbox carries its own. */
		label: string;
		required?: boolean;
		hint?: string;
		error?: string;
		children: Snippet<[{ id: string; describedBy: string | undefined; invalid: boolean }]>;
	}

	let { id, label, required = false, hint, error, children }: Props = $props();

	const hintId = $derived(`${id}-hint`);
	const errorId = $derived(`${id}-error`);
	const describedBy = $derived(
		[hint ? hintId : '', error ? errorId : ''].filter(Boolean).join(' ') || undefined
	);
</script>

<div class="space-y-2">
	{#if label}
		<label
			for={id}
			class="block text-xs font-medium tracking-widest text-muted-foreground uppercase"
		>
			{label}{#if required}<span class="text-primary" aria-hidden="true"> *</span>{/if}
		</label>
	{/if}
	{@render children({ id, describedBy, invalid: Boolean(error) })}
	{#if hint}
		<p id={hintId} class="text-xs text-muted-foreground">{hint}</p>
	{/if}
	{#if error}
		<p id={errorId} class="text-sm text-destructive">{error}</p>
	{/if}
</div>
