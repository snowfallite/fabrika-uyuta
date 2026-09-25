<script lang="ts">
	import { cn, type WithElementRef, type WithoutChildren } from '$lib/utils.js';
	import type { HTMLTextareaAttributes } from 'svelte/elements';
	import { fieldClass } from '../input/input.svelte';

	type Props = WithoutChildren<WithElementRef<Omit<HTMLTextareaAttributes, 'name'>>> & {
		name: string;
	};

	let {
		ref = $bindable(null),
		value = $bindable(),
		rows = 4,
		class: className,
		...restProps
	}: Props = $props();
</script>

<textarea
	bind:this={ref}
	data-slot="textarea"
	class={cn(fieldClass, 'resize-none', className)}
	{rows}
	bind:value
	{...restProps}></textarea>
