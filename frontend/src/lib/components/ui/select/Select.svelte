<script lang="ts">
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import { fieldClass } from '../input/input.svelte';

	interface Props {
		name: string;
		id?: string;
		options: { value: string; label: string }[];
		value?: string;
		/** Rendered as a disabled empty option. */
		placeholder?: string;
		required?: boolean;
		'aria-invalid'?: boolean;
		'aria-describedby'?: string;
	}

	let { value = $bindable(''), options, placeholder, ...rest }: Props = $props();
</script>

<div class="relative">
	<select bind:value class="{fieldClass} cursor-pointer appearance-none pr-8" {...rest}>
		{#if placeholder}
			<option value="" disabled>{placeholder}</option>
		{/if}
		{#each options as option (option.value)}
			<option value={option.value}>{option.label}</option>
		{/each}
	</select>
	<ChevronDown
		class="pointer-events-none absolute top-1/2 right-1 size-4 -translate-y-1/2 text-muted-foreground"
		aria-hidden="true"
	/>
</div>
