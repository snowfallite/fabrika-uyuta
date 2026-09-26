<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		name: string;
		id?: string;
		checked?: boolean;
		value?: string;
		required?: boolean;
		'aria-invalid'?: boolean;
		'aria-describedby'?: string;
		/** First invalid field after a no-JS submit (tech.md v6). */
		autofocus?: boolean;
		/** Label content; may contain links. */
		children: Snippet;
	}

	let { checked = $bindable(false), value = 'on', children, ...rest }: Props = $props();
</script>

<label class="flex cursor-pointer items-start gap-3 text-sm leading-relaxed text-foreground/85">
	<input
		type="checkbox"
		bind:checked
		{value}
		class="mt-0.5 size-5 shrink-0 cursor-pointer accent-primary aria-invalid:outline-2 aria-invalid:outline-destructive"
		{...rest}
	/>
	<span>{@render children()}</span>
</label>
