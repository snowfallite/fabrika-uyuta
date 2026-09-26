<script lang="ts" module>
	// Underline field from the template; shared by Textarea, Select and PhoneInput.
	export const fieldClass =
		'w-full min-w-0 border-0 border-b border-input bg-transparent py-2 text-base text-foreground transition-[border-color,box-shadow] outline-none placeholder:text-muted-foreground focus:border-primary focus:shadow-[0_1px_0_0_var(--primary)] disabled:cursor-not-allowed disabled:opacity-60 aria-invalid:border-destructive aria-invalid:focus:shadow-[0_1px_0_0_var(--destructive)]';
</script>

<script lang="ts">
	import { cn, type WithElementRef } from '$lib/utils.js';
	import type { HTMLInputAttributes } from 'svelte/elements';

	type Props = WithElementRef<
		Omit<HTMLInputAttributes, 'type' | 'name'> & {
			name: string;
			type?: 'text' | 'email' | 'tel';
		}
	>;

	let {
		ref = $bindable(null),
		value = $bindable(),
		type = 'text',
		class: className,
		...restProps
	}: Props = $props();
</script>

<input
	bind:this={ref}
	data-slot="input"
	class={cn(fieldClass, className)}
	{type}
	bind:value
	{...restProps}
/>
