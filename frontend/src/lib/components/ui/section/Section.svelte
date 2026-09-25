<script lang="ts">
	import type { Snippet } from 'svelte';
	import { cn } from '$lib/utils.js';
	import { Container } from '../container';

	interface Props {
		id?: string;
		title?: string;
		/** Eyebrow line above the title, as in the template. */
		subtitle?: string;
		tone?: 'default' | 'muted' | 'inverted';
		headingLevel?: 2 | 3;
		class?: string;
		children: Snippet;
	}

	let {
		id,
		title,
		subtitle,
		tone = 'default',
		headingLevel = 2,
		class: className,
		children
	}: Props = $props();

	const uid = $props.id();
	const headingId = $derived(`${id ?? uid}-title`);
</script>

<section
	{id}
	aria-labelledby={title ? headingId : undefined}
	class={cn(
		'py-24 md:py-32',
		tone === 'muted' && 'bg-secondary/40',
		tone === 'inverted' && 'bg-primary text-primary-foreground',
		className
	)}
>
	<Container>
		{#if title}
			<div class="mb-12 max-w-3xl">
				{#if subtitle}
					<p
						class={cn(
							'mb-4 text-xs font-medium tracking-widest uppercase',
							tone === 'inverted' ? 'text-primary-foreground/80' : 'text-muted-foreground'
						)}
					>
						{subtitle}
					</p>
				{/if}
				<svelte:element
					this={`h${headingLevel}`}
					id={headingId}
					class={cn(
						'text-4xl leading-[1.08] font-light text-balance sm:text-5xl lg:text-6xl',
						tone !== 'inverted' && 'text-primary'
					)}
				>
					{title}
				</svelte:element>
			</div>
		{/if}
		{@render children()}
	</Container>
</section>
