<script lang="ts">
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import Info from '@lucide/svelte/icons/info';
	import type { Snippet } from 'svelte';
	import { cn } from '$lib/utils.js';

	interface Props {
		tone: 'success' | 'error' | 'info';
		title?: string;
		children: Snippet;
	}

	let { tone, title, children }: Props = $props();

	const Icon = $derived({ success: CircleCheck, error: CircleAlert, info: Info }[tone]);
</script>

<div
	role={tone === 'error' ? 'alert' : 'status'}
	class={cn(
		'flex gap-3 rounded-2xl p-4 text-sm leading-relaxed',
		tone === 'success' && 'bg-primary/10 text-primary',
		tone === 'error' && 'border border-destructive/40 bg-background text-destructive',
		tone === 'info' && 'bg-secondary text-secondary-foreground'
	)}
>
	<Icon class="mt-0.5 size-5 shrink-0" aria-hidden="true" />
	<div class="space-y-1">
		{#if title}
			<p class="font-medium">{title}</p>
		{/if}
		<div>{@render children()}</div>
	</div>
</div>
